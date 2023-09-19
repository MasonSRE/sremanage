package api

import (
	"bingo_api/application/constants"
	"bingo_api/application/model"
	. "bingo_api/application/services"
	. "bingo_api/application/utils"
	"fmt"
	"github.com/gin-gonic/gin"
	"net/http"
	"strconv"
)

/**
添加主机类别
*/

func HostCategoryCreate(ctx *gin.Context) {
	hostCategory, err := CreateHostCategory(ctx)
	if err != nil || hostCategory.ID < 1 {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeCreateHostCategoryFail,
			"message": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"code":    constants.CodeSuccess,
		"message": constants.Success,
		"data": map[string]model.HostCategoryInstance{
			"hostCategory": hostCategory,
		},
	})
}

/**
获取所有主机类别
*/

func HostCategoryList(ctx *gin.Context) {
	// 调用业务层获取主机类别列表
	hostCategoryList, err := GetHostCategoryList(ctx)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeGetHostCategoryFail,
			"message": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"code":    constants.CodeSuccess,
		"message": constants.Success,
		"data": map[string][]model.HostCategoryInstance{
			"host_category_list": hostCategoryList,
		},
	})
}

/**
添加主机
*/

func HostCreate(ctx *gin.Context) {
	// 调用业务层创建主机信息
	host, err := CreateHost(ctx)
	if err != nil || host.ID < 1 {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeCreateHostFail,
			"message": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"code":    constants.CodeSuccess,
		"message": constants.Success,
		"data": map[string]interface{}{
			"host": host,
		},
	})
}

/**
主机列表
*/

func HostList(ctx *gin.Context) {
	// 接受参数
	name, _ := ctx.GetQuery("name")
	hostname, _ := ctx.GetQuery("host")
	hostCategoryId, _ := strconv.Atoi(ctx.Query("host_category_id"))
	hostList, err := GetHostList(name, uint(hostCategoryId), hostname)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeGetHostFail,
			"message": err.Error(),
		})
		return
	}
	ctx.JSON(http.StatusOK, gin.H{
		"code":    constants.CodeSuccess,
		"message": constants.Success,
		"data": map[string]interface{}{
			"host_list": hostList,
		},
	})
}

/*
删除主机
*/

func HostDelete(ctx *gin.Context) {
	// 接受参数
	idStr, _ := ctx.GetQuery("id")
	delId, _ := strconv.Atoi(idStr)
	host, err := DeleteHost(uint(delId))
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeDelHostFail,
			"message": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"code":    constants.CodeSuccess,
		"message": constants.Success,
		"data": map[string]interface{}{
			"delete_host": host,
		},
	})
}

/*websocket请求*/

func HostConsole(ctx *gin.Context) {
	// 一、准备阶段
	// 同意升级websocket请求
	ws, err := UpGrader.Upgrade(ctx.Writer, ctx.Request, nil)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeFail,
			"message": err.Error(),
		})
		return
	}

	// 根据ID获取主机连接信息
	id, err := strconv.Atoi(ctx.Param("id"))
	fmt.Println("id", id)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeFail,
			"message": err.Error(),
		})
		return
	}

	host := model.Host{}
	err = host.GetOneById(uint(int(id)))
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeFail,
			"message": err.Error(),
		})
		return
	}
	fmt.Println("host:::", host)

	// 创建SSh远程连接，
	cli := NewSSH(host.IpAddr, host.Username, "", host.PrivateKey, "key", int(host.Port))
	if err := cli.Connect(); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"code":    constants.CodeFail,
			"message": err.Error(),
		})
		return
	}
	fmt.Println("密钥登录成功！")
	// 二、实现一个web-ssh命令通信
	cli.Web2SSH(ws)

}
