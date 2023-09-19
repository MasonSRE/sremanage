package api

import (
	"bingo_api/application/constants"
	. "bingo_api/application/services"
	. "bingo_api/application/utils"
	"github.com/gin-gonic/gin"
	"net/http"
	"strconv"
)

/**
用户认证登陆
*/

/**
用户认证登陆
*/

func UserAuthenticate(ctx *gin.Context) {
	user, err := UserLogin(ctx)

	if err != nil || user.ID < 1 {
		ctx.JSON(http.StatusOK, gin.H{
			"code":    constants.CodeNoSuchUser,
			"message": err.Error(),
		})
		return
	}

	// 生成token
	newJwt := NewJWT()
	publicClaims := PublicClaims{
		ID:       strconv.Itoa(int(user.ID)),
		Username: user.Username,
		Nickname: user.Nickname,
		Avatar:   user.Avatar,
	}

	token, err := newJwt.AccessToken(publicClaims)
	if err != nil {
		panic(err.Error())
	}

	ctx.JSON(http.StatusCreated, gin.H{
		"code":    constants.CodeSuccess,
		"message": constants.Success,
		"data": map[string]interface{}{
			"token": token,
		},
	})
}

/**
创建用户
*/

func UserCreate(ctx *gin.Context) {

	id, err := CreateUser(ctx)
	if err != nil || id < 1 {
		ctx.JSON(http.StatusOK, gin.H{
			"code":    constants.CodeCreateUserFail,
			"message": constants.CreateUserFail,
			"err":     err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusCreated, gin.H{
		"code":    constants.CodeSuccess,
		"message": constants.CreateUserSuccess,
		"data":    id,
	})
}
