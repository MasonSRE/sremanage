package utils

import (
	"github.com/gorilla/websocket"
	"net/http"
)

var UpGrader = websocket.Upgrader{
	// 设置允许跨域进行ws通信
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}
