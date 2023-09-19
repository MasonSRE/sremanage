package validator

import (
	"bingo_api/application/config"
	"bingo_api/application/constants"
	. "bingo_api/application/model"
	. "bingo_api/application/utils"
	"errors"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"io/ioutil"
	"mime/multipart"
	"strconv"
	"strings"
)

/**
添加主机类别的验证器
*/

func HostCategoryValidator(hostCategory *HostCategory) error {
	validate, trans := GenValidate()
	err := validate.Struct(hostCategory)
	if err != nil {
		for _, err := range err.(validator.ValidationErrors) {
			return errors.New(err.Translate(trans))
		}
	}
	return nil
}

/**
添加主机的验证器
*/

func HostValidator(host *Host, ctx *gin.Context) error {
	// (1) 接收数据

	// 接收多文件上传的表单数据
	form, err := ctx.MultipartForm()
	if err != nil {
		return err
	}
	fmt.Println("form:::", form)

	// 手动接收表单信息并赋值
	// form.Value接收文本字段 form.File接收上传文件
	hostCategoryId, _ := strconv.Atoi(form.Value["host_category_id"][0])
	host.HostCategoryID = uint(hostCategoryId)
	port, _ := strconv.Atoi(form.Value["port"][0])
	host.Port = uint(port)
	host.Username = form.Value["username"][0]
	host.Password = form.Value["password"][0]
	host.Name = form.Value["name"][0]
	host.IpAddr = form.Value["ip_addr"][0]
	host.Remark = form.Value["remark"][0]
	fmt.Println("host:::", host)

	// (2) 校验数据
	// 校验基本规则
	validate, trans := GenValidate()
	err = validate.Struct(host)
	if err != nil {
		for _, err := range err.(validator.ValidationErrors) {
			fmt.Println("err:::", err)

			return errors.New(err.Translate(trans))
		}
	}

	// 校验类型范围
	if host.HostCategoryID < 1 {
		return errors.New(constants.HostCategoryNotExist)
	}

	var hostCategory HostCategory
	err = hostCategory.GetOneById(host.HostCategoryID)
	if err != nil {
		return errors.New(constants.HostCategoryNotExist)
	}
	// 校验主机是否可以ping通，可以的话，将公钥上传到服务器指定位置，方便后面的免密登录
	err = ping(host, form)
	if err != nil {
		return err
	}
	return nil
}

func ping(host *Host, form *multipart.Form) error {
	var err error

	// （1）获取公私钥
	// 从表单中提取上传文件
	keys := form.File["files[]"] // 务必与客户端上传时设置的字段名一致，否无接收不了
	// 根据上传文件个数判断
	if len(keys) == 1 {
		// 报错，允许上传一个文件
		return errors.New(constants.Missingkeys)
	} else if len(keys) == 2 {
		// 上传秘钥对两个文件
		// 获取第一个文件
		fileHandle1, err := keys[0].Open()
		if err != nil {
			return err
		}
		defer fileHandle1.Close()
		fileByte, _ := ioutil.ReadAll(fileHandle1)
		key1 := string(fileByte)

		// 获取第二个文件
		fileHandle2, err := keys[1].Open()
		defer fileHandle2.Close()
		fileByte, _ = ioutil.ReadAll(fileHandle2)
		key2 := string(fileByte)

		if strings.Contains(key1, "PRIVATE") { // 通过判断秘钥中的内容，区分公钥和私钥。
			host.PrivateKey, host.PublicKey = key1, key2
		} else {
			host.PrivateKey, host.PublicKey = key2, key1
		}

	} else {
		// todo 采用全局公私钥作为默认值
		host.PublicKey, host.PrivateKey = config.Conf.PublicKey, config.Conf.PrivateKey
	}

	// （2）确认好公私钥，创建ssh对象，进行ssh操作
	cli := NewSSH(host.IpAddr, host.Username, host.Password, "", "password", int(host.Port))
	// 基于密码首次SSH连接
	if err := cli.Connect(); err != nil {
		fmt.Println("err", err)
		return errors.New(constants.HostInfoEror)
	}
	fmt.Println("cli.Client:::", cli.Client)
	fmt.Println("host.PublicKey:::", host.PublicKey)

	// 验证主机信息成功以后，接下来就可以把公钥写入到远程主机了。
	if err := cli.AddPublicKeyToRemoteHost(host.PublicKey); err != nil {
		return errors.New(constants.SSHKeyIsInvalid)
	}

	return err

}
