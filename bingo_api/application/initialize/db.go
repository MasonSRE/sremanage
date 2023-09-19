package initialize

import (
	"bingo_api/application/config"
	"bingo_api/application/database"
	"bingo_api/application/model"
)

func InitDB(cfg *config.DatabaseConfig) {
	Orm := database.GetOrm(cfg)
	// 禁用复数
	Orm.SingularTable(true)
	// 数据迁移
	Orm.AutoMigrate(&model.User{})
	Orm.AutoMigrate(&model.HostCategory{})
	Orm.AutoMigrate(&model.Host{})
}
