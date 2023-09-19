package database

import (
	"bingo_api/application/config"
	"fmt"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql"
	"go.uber.org/zap"
	"time"
)

var Orm *gorm.DB

func GetOrm(cfg *config.DatabaseConfig) *gorm.DB {
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=%s&parseTime=true&loc=Local",
		cfg.Username,
		cfg.Password,
		cfg.Host,
		cfg.Port,
		cfg.Database,
		cfg.Charset)
	var err error
	Orm, err = gorm.Open(cfg.Driver, dsn)
	if err != nil {
		zap.S().Errorf("database connection fail: %v", err.Error())
		panic(err.Error())
	}
	// 最大链接数
	Orm.DB().SetMaxOpenConns(cfg.MaximumConn)
	// 最大空闲连接数
	Orm.DB().SetMaxIdleConns(cfg.MaximumFreeConn)
	// 每个链接的最大生命周期
	Orm.DB().SetConnMaxLifetime(time.Duration(cfg.TimeOut))
	if Orm.Error != nil {
		zap.S().Errorf("database error: %v", Orm.Error)
		panic(Orm.Error)
	}

	zap.S().Infof("mysql连接成功: %v", dsn)

	return Orm
}

/*
最大连接数（MaxOpenConns）：它限制了连接池中可以同时打开的连接数量。
通过设置最大连接数，可以防止过多的连接同时被创建，从而避免数据库服务器过载或资源耗尽的情况。
如果达到最大连接数限制，新的数据库连接请求将被阻塞，直到有连接被释放回连接池。

最大空闲连接数（MaxIdleConns）：它限制了连接池中可以保持空闲的连接数量。
连接池中的空闲连接可以避免频繁地创建和销毁连接，从而提高性能。
设置适当的最大空闲连接数可以根据应用程序的负载情况平衡连接的创建和销毁成本，确保连接池中始终有足够的连接供应用程序使用。

设置连接的最大生命周期可以确保连接在一段时间后被释放，以防止连接长时间保持打开状态而导致资源耗尽。
*/
