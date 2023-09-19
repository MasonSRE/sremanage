package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
)

func main() {
	// 头部信息
	/*headerData := map[string]string{
		"typ": "JWT",
		"alg": "HS256",
	}

	headerJson, _ := json.Marshal(headerData)
	headerBytes := []byte(string(headerJson))
	// base64编码:
	headerString := strings.TrimRight(base64.URLEncoding.EncodeToString(headerBytes), "=")
	fmt.Println(headerString)*/

	// base64解码
	headerString := "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
	headerBytes, _ := base64.URLEncoding.DecodeString(headerString)
	fmt.Println(string(headerBytes)) // {"alg":"HS256","typ":"JWT"}

	type Header struct {
		Alg string `json:"alg"`
		Typ string `json:"typ"`
	}

	header := Header{}
	json.Unmarshal(headerBytes, &header)
	fmt.Println(header)
}

// 各个语言中都有base64编码和解码的功能，所以我们jwt为了安全，需要配合第三段签证加密
