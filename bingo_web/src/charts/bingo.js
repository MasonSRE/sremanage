export const AlertChartOption = {
    title: {
        text: '本周预警次数',
        left: 'center'
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        }
    },
    toolbox: {
        show: true,
        feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            restore: { show: true },
            saveAsImage: { show: true }
        }
    },
    grid: {
        left: '2%',
        right: '2%',
        bottom: '1%',
        containLabel: true
    },
    xAxis: [
        {
            type: 'category',
            data: ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期天'],
            axisTick: {
                alignWithLabel: true
            }
        }
    ],
    yAxis: [
        {
            type: 'value'
        }
    ],
    series: [
        {
            name: '注意',
            type: 'bar',
            barWidth: '10%',
            data: [13, 12, 8, 16, 22, 20, 11]
        },
        {
            name: '警告',
            type: 'bar',
            barWidth: '10%',
            data: [5, 5, 12, 4, 0, 11, 2]
        },
        {
            name: '故障',
            type: 'bar',
            barWidth: '10%',
            data: [0, 1, 0, 2, 3, 1, 4]
        },
        {
            name: '严重',
            type: 'bar',
            barWidth: '10%',
            data: [2, 0, 1, 0, 0, 1, 2]
        }
    ]
};


export const HostChartOption = {
    title: {
        text: '主机信息',
        left: 'center'
    },
    tooltip: {
        trigger: 'item'
    },
    toolbox: {
        show: true,
        feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            restore: { show: true },
            saveAsImage: { show: true }
        }
    },
    legend: {
        top: 'bottom'
    },
    series: [
        {
            name: '主机信息',
            type: 'pie',
            radius: '60%',
            data: [
                { value: 45, name: '测试服务器' },
                { value: 25, name: 'web服务器' },
                { value: 15, name: '代理服务器' },
                { value: 14, name: '数据库服务器' },
                { value: 79, name: '未分类' }
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