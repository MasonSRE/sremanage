package config

import (
	"encoding/json"
	"fmt"
	"github.com/dgrijalva/jwt-go"
	"os"
)

// Config 整个项目的配置
type Config struct {
	Mode                string `json:"mode"`
	Host                string `json:"host"`
	Port                int    `json:"port"`
	SecretKey           string `json:"secret_key"`
	*LogConfig          `json:"log"`
	*DatabaseConfig     `json:"database"`
	*jwt.StandardClaims `json:"jwt"`
	*SSHGlobalKeys      `json:"ssh_global_keys"`
}

// LogConfig 日志配置
type LogConfig struct {
	Level      string `json:"level"`
	Filename   string `json:"filename"`
	MaxSize    int    `json:"maxsize"`
	MaxAge     int    `json:"max_age"`
	MaxBackups int    `json:"max_backups"`
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	Driver          string `json:"driver"`
	Host            string `json:"host"`
	Port            string `json:"port"`
	Database        string `json:"database"`
	Username        string `json:"username"`
	Password        string `json:"password"`
	Charset         string `json:"charset"`
	MaximumConn     int    `json:"maximum_connection"`
	MaximumFreeConn int    `json:"maximum_free_connection"`
	TimeOut         int    `json:"timeout"`
}

// SSHGlobalKeys SSH全局秘钥对
type SSHGlobalKeys struct {
	PrivateKeyPath string `json:"private_key_path"`
	PublicKeyPath  string `json:"public_key_path"`

	PrivateKey string `json:"private_key"`
	PublicKey  string `json:"public_key"`
}

// Conf 全局配置变量
var Conf = &Config{}

// Init 初始化配置；从指定文件加载配置文件
func InitConfig(filePath string) error {
	/**
	filePath 配置文件json文件的路径
	*/
	b, err := os.ReadFile(filePath)
	if err != nil {
		return err
	}

	err = json.Unmarshal(b, Conf)
	// 读取SSH全局秘钥对
	publicKey, _ := os.ReadFile(Conf.SSHGlobalKeys.PublicKeyPath)
	privateKey, _ := os.ReadFile(Conf.SSHGlobalKeys.PrivateKeyPath)
	Conf.SSHGlobalKeys.PublicKey = string(publicKey)
	Conf.SSHGlobalKeys.PrivateKey = string(privateKey)

	fmt.Println("publicKey:", Conf.SSHGlobalKeys.PublicKey)
	fmt.Println("privateKey:", Conf.SSHGlobalKeys.PrivateKey)
	return err
}
