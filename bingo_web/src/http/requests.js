import http from "./index.js";

// 获取站点配置信息
export const get_api_test = (params, headers) => {
    return http.get("test/", {params, headers})
};