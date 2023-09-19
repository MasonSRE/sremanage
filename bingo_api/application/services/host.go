package services

import (
	. "bingo_api/application/model"
	"bingo_api/application/validator"
	"fmt"
	"github.com/gin-gonic/gin"
)

/**
添加主机类别
*/

func CreateHostCategory(ctx *gin.Context) (HostCategoryInstance, error) {
	hostCategory := HostCategory{}
	var instance HostCategoryInstance
	var err error
	// （1）反序列化： 接收来自前端的数据
	if err = ctx.ShouldBindJSON(&hostCategory); err != nil {
		return instance, err
	}
	// （2）校验：校验前端传入的数据
	if err = validator.HostCategoryValidator(&hostCategory); err != nil {
		return instance, err
	}
	// （3）数据库操作
	err = hostCategory.Insert()
	// （4）序列化：json序列化响应
	instance = HostCategoryInstance{
		ID:   hostCategory.ID,
		Name: hostCategory.Name,
	}
	return instance, err
}

/**
获取主机类别列表
*/

func GetHostCategoryList(ctx *gin.Context) ([]HostCategoryInstance, error) {
	hostCategory := HostCategory{}
	hostCategoryList, err := hostCategory.GetAll()
	return hostCategoryList, err
}

/**
添加主机
*/

func CreateHost(ctx *gin.Context) (HostInstance, error) {
	host := Host{}
	var err error
	var hostCategory HostCategory
	var instance HostInstance
	// (1) 获取请求数据
	/*	if err = ctx.ShouldBindJSON(&host); err != nil {
			return instance, err
		}
		fmt.Println("host>>>", host)*/

	// (1)  数据获取和校验
	if err = validator.HostValidator(&host, ctx); err != nil {
		return instance, err
	}
	// (3) 数据库操作
	err = host.Insert()
	if err != nil {
		return instance, err
	}
	// (4) 序列化
	fmt.Println("插入数据库成功后的host:::", host)
	err = hostCategory.GetOneById(host.HostCategoryID)
	if err != nil {
		return instance, err
	}

	instance = HostInstance{
		ID:     host.ID,
		Name:   host.Name,
		IpAddr: host.IpAddr,
		Port:   host.Port,
		// Username:     host.Username,
		Remark:       host.Remark,
		CategoryID:   host.HostCategoryID,
		CategoryName: hostCategory.Name,
	}
	return instance, err
}

/**
获取主机列表信息
*/

func GetHostList(name string, hostCategoryId uint, hostname string) ([]HostInstance, error) {
	var hostList []Host
	var instanceList []HostInstance
	var host Host
	var err error
	hostList, err = host.GetAll(name, uint(hostCategoryId), hostname)
	fmt.Println("hostList:::", hostList)
	// host  [host01,host02,...]

	for _, hostItem := range hostList {
		hi := HostInstance{
			ID:     hostItem.ID,
			Name:   hostItem.Name,
			IpAddr: hostItem.IpAddr,
			Port:   hostItem.Port,
			// Username:     hostItem.Username,
			CategoryID:   hostItem.HostCategory.ID,
			CategoryName: hostItem.HostCategory.Name,
			Remark:       hostItem.Remark,
		}
		instanceList = append(instanceList, hi)
	}
	return instanceList, err
}

/**
删除主机列表信息
*/

func DeleteHost(hostId uint) (HostInstance, error) {
	var delHost Host
	var instance HostInstance

	err := delHost.GetOneById(hostId)
	if err != nil {
		return instance, err
	}
	err = delHost.Delete()
	if err != nil {
		return instance, err
	}

	instance = HostInstance{
		Name:   delHost.Name,
		IpAddr: delHost.IpAddr,
		Port:   delHost.Port,
		// Username:   delHost.Username,
		Remark:     delHost.Remark,
		CategoryID: delHost.HostCategoryID,
	}

	return instance, err
}
