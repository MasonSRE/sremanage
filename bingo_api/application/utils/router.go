package utils

import "github.com/gin-gonic/gin"

func Register(r *gin.RouterGroup, httpMethods []string, relativePath string, handlers ...gin.HandlerFunc) gin.IRoutes {
	/**
	路由注册函数[一次性给同一个视图绑定多个不同的HTTP请求方法]
	*/
	var routes gin.IRoutes
	for _, httpMethod := range httpMethods {
		routes = r.Handle(httpMethod, relativePath, handlers...)
	}
	return routes
}
