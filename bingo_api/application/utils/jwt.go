package utils

import (
	"bingo_api/application/config"
	. "bingo_api/application/constants"
	"errors"
	"github.com/dgrijalva/jwt-go"
	"time"
)

/**
JWT基本结构体
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
	Nickname string `json:"nickname"`
	Avatar   string `json:"avatar"`
	jwt.StandardClaims
}

/**
新建一个jwt实例
*/

func NewJWT() *JWT {
	return &JWT{
		[]byte(config.Conf.SecretKey),
	}
}

/**
生成一个AccessToken
*/

func (j *JWT) AccessToken(claims PublicClaims) (string, error) {
	// 获取当前时间
	now := time.Now()
	// 获取当前时间的Unix时间戳
	nowAt := now.Unix()
	// 设置token的签发时间
	claims.IssuedAt = nowAt
	// 设置jwt的唯一身份标识，主要用来作为一次性token,从而回避重放攻击。
	claims.Id = uuid4()
	// 判断：如果配置项中有设置token的过期时间
	if config.Conf.ExpiresAt > 0 {
		// 则在token的载荷信息中记录，当前token的起用时间和过期时间
		expAt := now.Add(time.Duration(config.Conf.ExpiresAt) * time.Second).Unix()
		claims.ExpiresAt = expAt
		claims.NotBefore = nowAt
	}
	// 判断：如果配置中有设置token的起用时间
	if config.Conf.NotBefore > 0 {
		// 则在token的载荷信息中记录，当前token的起用时间
		nbfAt := now.Add(time.Duration(config.Conf.NotBefore) * time.Second).Unix()
		claims.NotBefore = nbfAt
	}

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
				return nil, errors.New(TokenIsMalformed)
			} else if ve.Errors&jwt.ValidationErrorExpired != 0 {
				return nil, errors.New(TokenIsExpired)
			} else if ve.Errors&jwt.ValidationErrorNotValidYet != 0 {
				return nil, errors.New(TokenIsNotValidYet)
			} else {
				return nil, errors.New(TokenIsInvalid)
			}
		}
	}
	if claims, ok := token.Claims.(*PublicClaims); ok && token.Valid {
		return claims, nil
	}
	return nil, errors.New(TokenIsInvalid)
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
	return "", errors.New(TokenIsInvalid)
}
