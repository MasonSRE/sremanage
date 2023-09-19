package main

import (
	. "bingo_api/application/config"
	"bingo_api/application/initialize"
	"fmt"
	"go.uber.org/zap"
	"path/filepath"
)

func main() {
	// 路由映射
	router := initialize.InitRouter()
	// 配置文件
	dir, err := filepath.Abs(filepath.Dir("."))
	fmt.Println("dir:::")
	if err != nil {
		panic(err.Error())
	}
	// 配置初始化
	if err := InitConfig(fmt.Sprintf("%s/config.json", dir)); err != nil {
		panic(err.Error())
	}
	fmt.Println("Conf:::", Conf)

	// 日志初始化
	initialize.InitLogger(Conf.LogConfig)
	// zap 提供了一个S函数和L函数给我们开发者使用，调用S函数或L函数，可以得到一个全局的线程安全的logger对象
	zap.S().Infof("服务端启动...端口：%d", Conf.Port)
	// 数据库MySQL的配置
	initialize.InitDB(Conf.DatabaseConfig)
	// 监听端口
	router.Run(fmt.Sprintf("%s:%d", Conf.Host, Conf.Port))

}
