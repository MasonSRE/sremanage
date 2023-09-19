const storage = {
    state: {
        user: {},
        token: "",
        remember: false
    },
    getUserInfo() {
        console.log("this.state.token ???", this.state)
        if (this.state.token === "") {
            return false
        }
        let payload = this.state.token.split(".")[1]  // 载荷
        let payload_data = JSON.parse(atob(payload)) // 用户信息
        console.log("payload_data:::", payload_data)
        // 从jwt的载荷中提取用户信息
        let now = parseInt((new Date() - 0) / 1000);
        if (payload_data.exp === undefined) {
            // 没登录
            this.clearStorage()
            return {}
        }

        if (parseInt(payload_data.exp) < now) {
            // 过期处理
            this.clearStorage()
            return {}
        }
        return payload_data;
    },
    tokenHandle(token) {
        this.state.token = token;
        // 解析token，获取用户载荷
        this.state.user = this.getUserInfo()
        // 同步本地存储
        this.setStorage()

    },
    key: 'login',
    setStorage() {
        if (this.state.remember) {
            localStorage[this.key] = JSON.stringify(this.state)
        } else {
            sessionStorage[this.key] = JSON.stringify(this.state)
        }
    },
    getStorage() {
        console.log("localStorage[this.key]:::", localStorage[this.key])
        console.log("sessionStorage[this.key]:::", sessionStorage[this.key])

        if (localStorage[this.key] === undefined && sessionStorage[this.key] === undefined) {
            return {}
        }
        if (localStorage[this.key]) {
            this.state = JSON.parse(localStorage[this.key])
        } else {
            this.state = JSON.parse(sessionStorage[this.key])
        }
        console.log("state:::", this.state)
    },
    clearStorage() {

        this.state = {
            user: {},
            token: "",
            remember: false
        }
        localStorage.removeItem(this.key)
        sessionStorage.removeItem(this.key)

    }

}


export default storage