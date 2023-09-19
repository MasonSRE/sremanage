package main

import (
	"errors"
	"fmt"
	"github.com/dgrijalva/jwt-go"
	_ "github.com/dgrijalva/jwt-go"
	"time"
)

// 消息提示常量
const (
	TokenExpired     = "认证令牌过期！"
	TokenNotValidYet = "令牌尚未激活！"
	TokenMalformed   = "认证令牌格式有误！"
	TokenInvalid     = "无效的认证令牌！"
)

// SecretKey 秘钥
var (
	SecretKey string = "secret"
)

/**
JWT
*/

type JWT struct {
	SigningKey []byte
}

/**
载荷
*/

type PublicClaims struct {
	ID       string `json:"id"`
	Username string `json:"username"`
	jwt.StandardClaims
}

/**
新建一个jwt实例
*/

func NewJWT() *JWT {
	return &JWT{
		[]byte(GetSecretKey()),
	}
}

/**
获取SecretKey
*/

func GetSecretKey() string {

	return SecretKey
}

/**
生成一个AccessToken
*/

func (j *JWT) AccessToken(claims PublicClaims) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(j.SigningKey)
}

/**
从Token中提取载荷
*/

func (j *JWT) GetPayloadByToken(tokenString string) (*PublicClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &PublicClaims{}, func(token *jwt.Token) (interface{}, error) {
		return j.SigningKey, nil
	})
	if err != nil {
		if ve, ok := err.(*jwt.ValidationError); ok {
			if ve.Errors&jwt.ValidationErrorMalformed != 0 {
				return nil, errors.New(TokenMalformed)
			} else if ve.Errors&jwt.ValidationErrorExpired != 0 {
				return nil, errors.New(TokenExpired)
			} else if ve.Errors&jwt.ValidationErrorNotValidYet != 0 {
				return nil, errors.New(TokenNotValidYet)
			} else {
				return nil, errors.New(TokenInvalid)
			}
		}
	}
	if claims, ok := token.Claims.(*PublicClaims); ok && token.Valid {
		return claims, nil
	}
	return nil, errors.New(TokenInvalid)
}

/**
更新token
*/

func (j *JWT) RefreshToken(tokenString string) (string, error) {
	jwt.TimeFunc = func() time.Time {
		return time.Unix(0, 0)
	}
	token, err := jwt.ParseWithClaims(tokenString, &PublicClaims{}, func(token *jwt.Token) (interface{}, error) {
		return j.SigningKey, nil
	})
	if err != nil {
		return "", err
	}
	if claims, ok := token.Claims.(*PublicClaims); ok && token.Valid {
		jwt.TimeFunc = time.Now
		println(time.Now().Add(1 * time.Hour).Unix())
		claims.StandardClaims.ExpiresAt = time.Now().Add(1 * time.Hour).Unix()
		return j.AccessToken(*claims)
	}
	return "", errors.New(TokenInvalid)
}

func main() {
	publicClaims := PublicClaims{
		ID:       "1",
		Username: "yuan",
	}
	newJwt := NewJWT()
	token, _ := newJwt.AccessToken(publicClaims)
	println(token)

	refreshToken, _ := newJwt.RefreshToken(token)
	fmt.Println("refresh token:", refreshToken)

}
