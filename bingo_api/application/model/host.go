package model

import (
	. "bingo_api/application/database"
	"github.com/jinzhu/gorm"
)

/**
主机类别实体
*/

type HostCategory struct {
	gorm.Model
	// 唯一索引 unique_index
	Name string `validate:"required,gte=2" json:"name" gorm:"type:varchar(255); unique_index"`
}

type HostCategoryInstance struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}

/**
设置表名
*/

func (category HostCategory) TableName() string {
	return "host_category"
}

/**
添加主机类别
*/

func (category *HostCategory) Insert() error {
	err := Orm.Create(&category).Error
	return err
}

/**
获取主机分类列表
*/

func (category HostCategory) GetAll() ([]HostCategoryInstance, error) {
	var categories []HostCategoryInstance
	err := Orm.Table(category.TableName()).Order(" id DESC ").Select("id, name").Scan(&categories).Error
	return categories, err
}

/**
根据指定ID获取主机类别
*/

func (category *HostCategory) GetOneById(id uint) error {
	err := Orm.First(&category, id).Error
	return err
}

/**
主机信息模型
*/

type Host struct {
	gorm.Model
	Name           string       `validate:"required,gte=2" json:"name" gorm:"type:varchar(255)"`
	IpAddr         string       `validate:"required,ipv4" json:"ip_addr" gorm:"type:varchar(255)"`
	Port           uint         `json:"port" gorm:"type:int"`
	Username       string       `json:"username" gorm:"varchar(255)"`
	Password       string       `json:"password,omitempty" gorm:"varchar(255)"`
	Remark         string       `json:"remark,omitempty" gorm:"varchar(255)"`
	HostCategoryID uint         `json:"host_category_id"`
	HostCategory   HostCategory `validate:"-" json:"host_category"  gorm:"foreignKey:HostCategoryID;references:ID"`
	PrivateKey     string       `json:"private_key,omitempty" gorm:"type:text"`
	PublicKey      string       `json:"public_key,omitempty" gorm:"type:text"`
}

type HostInstance struct {
	ID     uint   `json:"id"`
	Name   string `json:"name"`
	IpAddr string `json:"ip_addr"`
	Port   uint   `json:"port"`
	// Username     string `json:"username"`
	CategoryID   uint   `json:"category_id"`
	CategoryName string `json:"category_name"`
	Remark       string `json:"remark"`
}

/**
设置表名
*/

func (host Host) TableName() string {
	return "host_info"
}

/**
添加主机
*/

func (host *Host) Insert() error {
	err := Orm.Create(&host).Error
	return err
}

/**
获取所有主机列表
*/

func (host Host) GetAll(name string, hostCategoryId uint, IpAddr string) ([]Host, error) {
	var hosts []Host
	query := Orm.Table(host.TableName())
	if name != "" {
		query = query.Where(" name LIKE ? ", "%"+name+"%")
	}
	if hostCategoryId > 0 {
		query = query.Where(" host_category_id = ? ", hostCategoryId)
	}
	if IpAddr != "" {
		query = query.Where(" ip_addr LIKE ? ", "%"+IpAddr+"%")
	}

	err := query.Order(" id DESC ").Preload("HostCategory").Find(&hosts).Error
	return hosts, err
}

/**
根据指定ID获取主机
*/

func (host *Host) GetOneById(id uint) error {
	err := Orm.First(&host, id).Error
	return err
}

/**
删除主机
*/

func (host *Host) Delete() (err error) {
	err = Orm.Delete(&host).Error
	return err
}
