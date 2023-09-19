package router

import (
	"bingo_api/application/api"
	"bingo_api/application/utils"
	"github.com/gin-gonic/gin"
)

func InitHostRouter(Router *gin.RouterGroup) {
	/**
	主机相关的路由组
	*/
	HostRouter := Router.Group("host")
	// HostRouter.Use(middleware.JWTAuthorization())
	{
		// 用户认证登陆
		HostRouter.POST("/", api.HostCreate)
		HostRouter.GET("/", api.HostList)

		// 主机类别-添加
		utils.Register(HostRouter, []string{"POST"}, "category", api.HostCategoryCreate)
		// 主机类别-查看
		utils.Register(HostRouter, []string{"GET"}, "category", api.HostCategoryList)
		// 主机 - 列表
		utils.Register(HostRouter, []string{"GET"}, "", api.HostList)
		// 主机 - 删除
		utils.Register(HostRouter, []string{"DELETE"}, "", api.HostDelete)
		// 主机 - console功能
		utils.Register(HostRouter, []string{"GET"}, ":id/console", api.HostConsole)

	}

}
