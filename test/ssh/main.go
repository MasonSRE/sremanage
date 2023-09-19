package main

import (
	"fmt"
	"os"
	"ssh_test/utils"
)

func main() {
	Host := "10.211.55.3"
	User := "root"
	Password := "yuan0316"
	Port := 22
	Key := ""
	Mode := "password"

	// 首次SSH连接使用密码
	cli := utils.NewSSH(Host, User, Password, Key, Mode, Port)
	fmt.Println(cli.Password, cli.Username, cli.IP, cli.Mode)
	if err := cli.Connect(); err != nil {
		print("连接失败！", err.Error())
		print("ssh client:::", cli.Client)
		return
	} else {
		print("连接成功！")
	}

	publicKey, _ := os.ReadFile("./keys/id_rsa.pub") // 这里放公钥字符串
	fmt.Println("publicKey:::", string(publicKey))
	err := cli.AddPublicKeyToRemoteHost(string(publicKey)) // 将本地的公钥发送到远程服务器的指定位置
	if err != nil {
		panic(err)
	}

}

/*package main

import (
	"fmt"
	"os"
	"ssh_test/utils"
)

func main() {
	Host := "10.211.55.3"
	User := "root"
	Password := "yuan0316"
	Port := 22
	Key := ""

	// 第2次以后采用秘钥连接
	Mode := "key"
	Password = ""

	privateKey, _ := os.ReadFile("./keys/id_rsa") // 这里放公钥字符串

	Key = string(privateKey)

	cli := utils.NewSSH(Host, User, Password, Key, Mode, Port)

	if err := cli.Connect(); err != nil {
		fmt.Printf("连接失败:%v", err)
		return
	} else {
		print("连接成功！\n")
	}

	defer cli.Client.Close()

	output, err := cli.Run("rm -rf apple.txt")
	if err != nil {
		print("执行失败！")
	}
	fmt.Printf("output:\n%v", output)
}
*/
