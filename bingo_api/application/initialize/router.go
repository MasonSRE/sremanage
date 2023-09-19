package initialize

import (
	. "bingo_api/application/middleware"
	. "bingo_api/application/router"
	"github.com/gin-gonic/gin"
)

func InitRouter() *gin.Engine {

	// 1. 创建路由
	Router := gin.Default()
	// 使用日志中间件
	Router.Use(GinLogger())
	Router.Use(ExceptionMiddleware)
	Router.Use(CORS)
	// Router.Use(JWTAuthorization())
	// 2. test路由分组
	TestGroup := Router.Group("/test")
	TestGroup.GET("/", func(context *gin.Context) {
		//panic("an error!!!")
		context.String(200, "Bingo Test")
	})

	APIGroup := Router.Group("/api")
	// APIGroup.Use(JWTAuthorization())
	// 初始化用户路由
	InitUserRouter(APIGroup)
	// 初始化主机路由
	InitHostRouter(APIGroup)

	return Router
}
