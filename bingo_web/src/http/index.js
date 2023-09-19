import axios from "axios";
import settings from "../settings";
import storage from "../utils/storage.js";

const http = axios.create({
    baseURL: settings.host,
    withCredentials: false,
})

// 请求拦截器
http.interceptors.request.use((config) => {
    console.log("http请求之前进行请求头组装，会自动执行请求拦截器");
    config.headers.Authorization = storage.state.token

    return config;
}, (error) => {
    console.log("http请求之后发生错误，会自动执行请求拦截器");
    return Promise.reject(error);
});


// 响应拦截器
http.interceptors.response.use((response) => {
    console.log("服务端响应数据以后在执行then之前，会自动执行响应拦截器");
    return response;
}, (error) => {
    console.log("服务端响应错误以后在执行catch之前，会自动执行响应拦截器");
    return Promise.reject(error);
});

export default http;