import {createRouter, createWebHistory} from 'vue-router'
import storage from "../utils/storage.js";
import Console from '../views/Console.vue'

const routes = [
    // { path: '/', name: 'Bingo', component: ()=>import("../views/Bingo.vue")},
    // { path: '/host', name: 'Host', component: ()=>import("../views/Host.vue")},
    // { path: '/bingo', name: 'Base', component: ()=>import("../views/Base.vue")},

    {
        path: '/bingo',
        name: 'Base', component: () => import("../views/Base.vue"),
        children: [
            {
                path: '',
                meta: {
                    title: "面板管理",
                    authorization: false
                },
                name: 'bingo',
                component: () => import("../views/Bingo.vue")
            },
            {
                path: 'manage/host',
                meta: {
                    title: "主机管理",
                    authorization: true
                },
                name: 'host', component: () => import("../views/Host.vue")
            },


            {
                meta: {
                    title: '远程主机管理',
                    authentication: true
                },
                path: 'host/console/:id', // :id 就是当前点击的主机信息的ID主键
                name: 'Console',
                component: Console
            },
        ]
    },

    {
        path: '/',
        name: 'login',
        meta: {
            title: "登录认证",
            authorization: false
        },

        component: () => import("../views/Login.vue")
    },

]

const router = createRouter({
    history: createWebHistory(),
    routes
});

// 路由保安
router.beforeEach((to, from, next) => {
    console.log("from:", from)
    console.log("to:", to)
    document.title = to.meta.title
    // 同步备份的认证数据
    storage.getStorage()
    console.log("to.meta authorization:::", to.meta.authorization)
    if (to.meta.authorization && !storage.getUserInfo()) {
        // 没有token，去登录页面
        next({"name": "login"})
    }

    next()
});


export default router;