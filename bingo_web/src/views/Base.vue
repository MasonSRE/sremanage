<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible>
      <div class="logo">
        <span>bingo</span>
      </div>
      <a-menu v-for="menu in menu_list" v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
        <a-menu-item v-if="menu.children.length===0" :key="menu.id">
          <router-link :to="menu.menu_url">
            <desktop-outlined/>
            <span> {{ menu.title }}</span>
          </router-link>
        </a-menu-item>
        <a-sub-menu v-else :key="menu.id">
          <template #title>
            <span>
              <user-outlined/>
              <span>{{ menu.title }}</span>
            </span>
          </template>
          <a-menu-item v-for="child_menu in menu.children" :key="child_menu.id">
            <router-link :to="child_menu.menu_url">{{ child_menu.title }}</router-link>
          </a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff;text-align: center">
        <a-row>
          <a-col :span="2" :offset="22">
            <a-dropdown placement="bottom">
              <p class="user"><UserOutlined /> root</p>
              <template #overlay>
                <a-menu>
                  <a-menu-item><LockOutlined/> 修改密码</a-menu-item>
                  <a-menu-item @click="logout"><LogoutOutlined/>退出登陆</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-col>
        </a-row>
      </a-layout-header>
      <a-layout-content style="margin: 0 16px">
        <a-breadcrumb style="margin: 16px 0">
          <a-breadcrumb-item><a href="">首页</a></a-breadcrumb-item>
          <a-breadcrumb-item>信息面板</a-breadcrumb-item>
        </a-breadcrumb>
        <div :style="{ padding: '24px', background: '#fff', minHeight: '550px'}">
          <router-view></router-view>

        </div>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        <p>Copyright © 2023 bingo</p>
        Power By <a href="">LinMo Jiang &amp; Bazinga Yuan</a>
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>
<script setup>
import { LogoutOutlined, LockOutlined, DesktopOutlined, UserOutlined} from '@ant-design/icons-vue';
import { ref } from 'vue';
import storage from '../utils/storage.js'
import router from '../router'
const collapsed = ref(false);
const selectedKeys = ref(['1']);

const menu_list = ref([
  {
    id: 1, icon: 'mail', title: '信息面板', menu_url: '/bingo', children: []
  },
  {
    id: 2, icon: 'mail', title: '资产管理', menu_url: '/bingo/manage', children: [
      {id: 9, icon: 'mail', title: '主机管理', menu_url: '/bingo/manage/host'},
      {id: 10, icon: 'mail', title: 'DB管理', menu_url: '/bingo/manage/db'},
      {id: 11, icon: 'mail', title: 'IDC机房', menu_url: '/bingo/manage/idc'},
      {id: 12, icon: 'mail', title: '资产配置', menu_url: '/bingo/manage/config'},
    ]
  },
  {
    "id": 3, icon: 'bold', title: '作业管理', menu_url: '/bingo/work', children: [
      {id: 13, icon: 'mail', title: '批量任务', menu_url: '/bingo/work/tasks'},
      {id: 14, icon: 'mail', title: '计划任务', menu_url: '/bingo/work/cron', children: []},
      {id: 15, icon: 'mail', title: '任务模板', menu_url: '/bingo/work/template'},
    ]
  },
  {
    id: 4, icon: 'highlight', title: '代码管理', menu_url: '/bingo/code', children: [
      {id: 16, icon: 'mail', title: '应用管理', menu_url: '/bingo/code/app'},
      {id: 17, icon: 'mail', title: '发布申请', menu_url: '/bingo/code/release'},
      {id: 18, icon: 'mail', title: '代码仓库', menu_url: '/bingo/code/repo'},
      {id: 19, icon: 'mail', title: '镜像仓库', menu_url: '/bingo/code/image'},
    ]
  },
  {
    id: 5, icon: 'mail', title: '配置管理', menu_url: '/bingo/config', children: [
      {id: 20, title: '环境管理', menu_url: '/bingo/config/env'},
      {id: 21, title: '服务配置', menu_url: '/bingo/config/services'},
      {id: 22, title: '应用配置', menu_url: '/bingo/config/app'}
    ]
  },
  {
    id: 6, icon: 'mail', title: '监控预警', menu_url: '/bingo/monitor', children: [
      {id: 23, title: '报警历史', menu_url: '/bingo/monitor/history'},
      {id: 24, title: '报警联系人', menu_url: '/bingo/monitor/user'},
      {id: 25, title: '报警联系组', menu_url: '/bingo/monitor/group'}
    ]
  },
  {
    id: 7, icon: 'mail', title: '用户管理', menu_url: '/bingo/auth', children: [
      {id: 26, title: '账户管理', menu_url: '/bingo/auth/user'},
      {id: 27, title: '角色管理', menu_url: '/bingo/auth/role'},
      {id: 28, title: '权限管理', menu_url: '/bingo/auth/permission'},
      {id: 29, title: '菜单管理', menu_url: '/bingo/auth/menu'},
    ]
  },
  {
    id: 8, icon: 'mail', title: '系统设置', menu_url: '/bingo/sys', children: []
  },
])


const logout = () => {

  storage.clearStorage()
  router.push("/")
}

</script>

<style>
.logo {
  font-style: italic;
  text-align: center;
  font-size: 20px;
  color:#fff;
  margin: 0 0 10px;
  line-height: 42px;
  height: 42px;
  background: rgba(255, 255, 255, 0.1);
}
.user{
  position: relative;
}
.user:after{
  content: "";
  border: 4px solid transparent;
  border-top: 4px solid #000;
  position: absolute;
  width: 0;
  height: 0;
  top: 30px;
  right: 12px;
  margin: auto;
}

</style>