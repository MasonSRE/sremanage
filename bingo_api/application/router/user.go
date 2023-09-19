package router

import (
	. "bingo_api/application/api"
	"bingo_api/application/middleware"
	. "bingo_api/application/utils"
	"github.com/gin-gonic/gin"
)

func InitUserRouter(r *gin.RouterGroup) {

	r.POST("/user", middleware.JWTAuthorization(), UserCreate) // 	r.Handle("POST","/user",UserCreate)
	Register(r, []string{"POST"}, "/user/authenticate", UserAuthenticate)
}
