package services

import (
	"bingo_api/application/constants"
	. "bingo_api/application/model"
	. "bingo_api/application/utils"
	. "bingo_api/application/validator"
	"errors"
	"fmt"
	"github.com/gin-gonic/gin"
)

/**
用户登录认证
*/

func UserLogin(ctx *gin.Context) (user User, err error) {
	user = User{}
	if err = ctx.ShouldBindJSON(&user); err != nil {
		return user, err
	}

	// 校验输入字段
	if err = UserValidator(&user); err != nil {
		return user, err
	}

	user.GetOneByAccount(user.Username)
	if user.ID < 1 {
		return user, errors.New(constants.NoSuchUser)
	}

	ret := CheckPassword(user.HashPassword, user.Password)

	if !ret {
		err = errors.New(constants.PasswordError)
		return
	}

	return
}

/**
创建用户
*/

func CreateUser(ctx *gin.Context) (uint, error) {
	// 接收数据
	user := User{}
	var err error
	if err = ctx.ShouldBindJSON(&user); err != nil {
		return 0, err
	}
	fmt.Println("user:::::", user)

	// 数据校验 validate组件

	// 校验输入字段
	if err = UserValidator(&user); err != nil {
		return 0, err
	}

	// 数据处理
	user.HashPassword, err = MakeHashPassword(user.Password)
	if err != nil {
		return 0, err
	}

	// 数据库操作
	return user.Insert()
}

/**
获取指定ID的用户
*/

func GetUserById(id uint) (user User) {
	user = User{}
	user.GetOneById(id)
	return user
}

/**
根据账户信息(用户名、手机、邮箱)获取用户
*/

func GetUserByAccount(account string) (user User) {
	user = User{}
	user.GetOneByAccount(account)
	return user
}

/**
获取所有用户
*/

func GetAllUser() []User {
	user := User{}
	return user.GetAll()
}

/**
更新密码
*/

func ChangeUserPassword(user User, RawPassword string) {
	password, _ := MakeHashPassword(RawPassword)
	user.ChangePassword(password)
}
