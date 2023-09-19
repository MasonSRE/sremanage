package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"net/http"
)

var upGrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

// webSocket请求ping 返回pong
func ping(c *gin.Context) {
	//升级get请求为webSocket协议
	ws, err := upGrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		return
	}

	defer func(ws *websocket.Conn) {
		_ = ws.Close()
	}(ws)

	ws.WriteMessage(1, []byte("welcome back"))

	for {
		// 读取ws中的数据
		mt, message, err := ws.ReadMessage()
		fmt.Println("mt:::", mt)
		if err != nil {
			break
		}
		fmt.Println("message::::", string(message))
		if string(message) == "ping" {
			message = []byte("pong")
		} else {
			message = []byte("口号不对！")
		}
		//写入ws数据
		err = ws.WriteMessage(mt, message)
		if err != nil {
			break
		}
	}

}

func main() {
	bindAddress := "localhost:9999"
	r := gin.Default()
	r.GET("/ping", ping)
	r.Run(bindAddress)
}
