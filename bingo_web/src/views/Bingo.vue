<!--
<template>
  <h3 @click="foo()">面板组件</h3>
  <a-button type="primary">Primary Button</a-button>
  <div class="chart" ref="chart01"></div>

</template>

<script setup>
import * as echarts from 'echarts';
import {ref,onMounted} from 'vue';
const chart01 = ref()

const foo = function () {
  // alert(123)
  // console.log(chart01.value)
}


onMounted(() => {

  // 初始化动作
  var myChart = echarts.init(chart01.value);
  var option;

  option = {
    title: {
      text: 'Referer of a Website',
      subtext: 'Fake Data',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: 'Access From',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 1048, name: 'Search Engine' },
          { value: 735, name: 'Direct' },
          { value: 580, name: 'Email' },
          { value: 484, name: 'Union Ads' },
          { value: 300, name: 'Video Ads' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  myChart.setOption(option);

})


</script>

<style scoped>
.chart {
  width: 500px;
  height: 300px;
  border: 1px solid rebeccapurple;
}
</style>-->
<template>
  <a-row class="top">
    <a-col class="item" :span="6">
      <div class="item-box">
        <usergroup-add-outlined class="icon-style" />
        <p>用户管理</p>
      </div>
    </a-col>
    <a-col class="item" :span="6">
      <div class="item-box">
        <fund-outlined class="icon-style" />
        <p>资产管理</p>
      </div>
    </a-col>
    <a-col class="item" :span="6">
      <div class="item-box">
        <clock-circle-outlined class="icon-style" />
        <p>任务中心</p>
      </div>
    </a-col>
    <a-col class="item" :span="6">
      <div class="item-box">
        <alert-outlined class="icon-style" />
        <p>告警通知</p>
      </div>
    </a-col>
  </a-row>
  <!-- 预警图表与主机信息图表 -->
  <a-row class="data-list">
    <a-col :span="12" class="item">
      <div class="item-box">
        <div class="alert-chart" ref="alert"></div>
      </div>
    </a-col>
    <a-col :span="12" class="item">
      <div class="item-box">
        <div class="host-chart" ref="host"></div>
      </div>
    </a-col>
    <a-col :span="14" class="task-data item">
      <div class="item-box">
        <a-table :columns="taskColumns" :data-source="taskData" :pagination="false">
          <template #headerCell="{ column }">
            <template v-if="column.key === 'title'">
              <span>
                <clock-circle-outlined />
                {{column.title}}
              </span>
            </template>
          </template>

          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'user'">
              <a>
                {{ record.user }}
              </a>
            </template>
            <template v-else-if="column.key === 'status'">
              <a-tag :color="['blue','green','orange','red'][record.status]">
                {{['暂停', '运行', '警告','错误'][record.status]}}
              </a-tag>
            </template>
          </template>
        </a-table>
      </div>
    </a-col>
    <a-col :span="8" class="item">
      <div class="item-box timeline">
        <a-timeline>
          <a-timeline-item>2015-09-01 08:03:23 王晓君登陆</a-timeline-item>
          <a-timeline-item>2015-09-01 09:30:01 赵川登陆</a-timeline-item>
          <a-timeline-item>2015-09-01 09:59:41 赵川登陆</a-timeline-item>
          <a-timeline-item>2015-09-01 15:03:06 王晓君登陆</a-timeline-item>
        </a-timeline>
      </div>
    </a-col>
  </a-row>
</template>

<script setup>
import {UsergroupAddOutlined, FundOutlined,ClockCircleOutlined, AlertOutlined, SmileOutlined, DownOutlined} from '@ant-design/icons-vue';
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import {AlertChartOption, HostChartOption} from "../charts/bingo.js";

// 预警图表
const alert = ref()
// 主机图表
const host = ref()

onMounted(()=>{
  echarts.init(alert.value).setOption(AlertChartOption);
  echarts.init(host.value).setOption(HostChartOption);

  // ajax请求数据，渲染数据
  

})

const taskColumns = [{
  title: '任务ID',
  dataIndex: 'id',
  key: 'id',
}, {
  title: '任务名',
  dataIndex: 'title',
  key: 'title',
}, {
  title: '用户',
  dataIndex: 'user',
  key: 'user',
}, {
  title: 'Status',
  dataIndex: 'status',
  key: 'status',
}];

const taskData = [{
  key: '1',
  id: 1,
  title: '巡检测试服务器',
  user: '王晓君',
  status: 1,
}, {
  key: '2',
  id: 2,
  title: '定时备份',
  user: '王晓君',
  status: 0,
}, {
  key: '3',
  id: 3,
  title: '发布xxx项目',
  user: '王晓君',
  status: 2,
}, {
  key: '4',
  id: 4,
  title: 'xxxxxx',
  user: '王晓君',
  status: 3,
}];

</script>

<style scoped>
/* 子组件中所有的css样式，都应该是局部的，只作用于当前组件，所以需要设置scoped属性 */
.top {
  margin: 10px 20px;
  box-shadow: 0 0 2px rgba(0,0,0,.125), 0 1px 3px rgba(0,0,0,.2);
}
.top .item {
  width: 60px;
  text-align: center;
  padding: 10px 0;
  cursor: pointer;
}
.item-box{
  border-radius: 5px;
  background: #fff;
  transition: all .5s linear;
}
.top .item-box:hover{
  background: #ff5500;
}
.top .item-box:hover .icon-style{
  color: #f0f0f0;
}
.top .item-box:hover p {
  color: #f0f0f0;
}
.icon-style{
  font-size: 32px;
  color: #ff5500;
}
.top .item p{
  margin-top: 10px;
}
.data-list{
  margin: 10px 20px;
  box-shadow: 0 0 1px rgba(0,0,0,.125), 0 1px 3px rgba(0,0,0,.2);
}
.alert-chart{
  width: 100%;
  height: 300px;
}

.host-chart{
  width: 100%;
  height: 300px;
}
.item-box{
  margin: 10px;
  padding-top: 20px;
  padding-bottom: 20px;
}

.timeline{
  padding-left: 20px;
}
</style>