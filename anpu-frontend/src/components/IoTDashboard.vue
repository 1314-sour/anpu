<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
// 确保 china.js 路径正确，如果之前下载没问题，这里就能正常引用

const timeHM = ref('');
const dateYMD = ref('');
let clockTimer = null;
let alarmInterval = null;

// --- 1. 还原效果图中的数据 ---
const deviceStats = ref([
  { id: 1, name: '监控设备', online: 120, total: 125, icon: '📹' },
  { id: 2, name: '消防设备', online: 85, total: 85, icon: '🧯' },
  { id: 3, name: '安全生产', online: 200, total: 212, icon: '🛡️' },
  { id: 4, name: '其他设备', online: 45, total: 53, icon: '📡' },
]);

const alarmStats = ref([
  { name: '高危报警', value: 12, icon: '🔴', color: '#ff4d4d' },
  { name: '中危报警', value: 35, icon: '🟠', color: '#ffd93d' },
  { name: '低危报警', value: 58, icon: '🔵', color: '#00d4ff' },
]);

const alarmList = ref([]);
const selectedDevice = ref({});
const showMapPopup = ref(false);

const mapContainer = ref(null);
const barChartContainer = ref(null);
const lineChartContainer = ref(null);
const donutChartContainer = ref(null);
const radarChartContainer = ref(null);

let mapChart, barChart, lineChart, donutChart, radarChart;

// --- 2. 还原图表配置 ---
const commonChartOption = {
  backgroundColor: 'transparent',
  textStyle: { color: '#fff' },
  grid: { top: '20%', bottom: '10%', left: '10%', right: '5%', containLabel: true },
  tooltip: { trigger: 'axis' }
};

// 修改 initMap 函数，使用最稳定的 npm 镜像源
const initMap = () => {
  if (!mapContainer.value) return;
  mapChart = echarts.init(mapContainer.value);
  
  mapChart.showLoading(); 

  // --- 修复点：使用 echarts 4.9.0 版本的官方文件，这个地址永久有效 ---
  fetch('https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/json/china.json')
    .then(response => {
        if (!response.ok) {
            throw new Error('网络请求失败，状态码：' + response.status);
        }
        return response.json();
    })
    .then(geoJson => {
      mapChart.hideLoading();
      
      echarts.registerMap('china', geoJson);

      mapChart.setOption({
        ...commonChartOption,
        geo: {
          map: 'china',
          roam: true,
          zoom: 1.2,
          label: { show: false },
          itemStyle: {
            areaColor: '#0a1a33', borderColor: '#1d4f7a', borderWidth: 1.5,
            shadowColor: 'rgba(0, 212, 255, 0.5)', shadowBlur: 10
          },
          emphasis: { itemStyle: { areaColor: '#1d4f7a' } }
        },
        series: [{
          type: 'effectScatter',
          coordinateSystem: 'geo',
          data: [
            { name: '设备 A-01', value: [116.40, 39.90], details: { type: '监控', status: '正常', temp: '35℃' } },
            { name: '设备 B-02', value: [121.47, 31.23], details: { type: '消防', status: '异常', temp: '60℃' } },
            { name: '内蒙古', value: [111.73, 40.83], details: { type: '安全', status: '正常', temp: '28℃' } }
          ],
          symbolSize: 15,
          itemStyle: { color: '#00d4ff', shadowBlur: 10, shadowColor: '#00d4ff' },
          rippleEffect: { scale: 4, brushType: 'stroke' }
        }]
      });
      
      mapChart.on('click', (params) => {
        if (params.componentType === 'series') {
          selectedDevice.value = { name: params.name, ...params.data.details };
          showMapPopup.value = true;
        } else {
          showMapPopup.value = false;
        }
      });
    })
    .catch(err => {
      console.error('地图加载失败:', err);
      mapChart.hideLoading();
      // 如果连这个都加载不了，说明公司网络屏蔽了所有 CDN
      // 那就只能回到下载文件的老路上了
      mapChart.setOption({
          graphic: {
              type: 'text',
              left: 'center',
              top: 'center',
              style: {
                  text: '无法连接外部网络，请联系管理员\n或下载 china.json 到本地',
                  fill: '#fff',
                  fontSize: 14
              }
          }
      });
    });
};

const initCharts = () => {
  // 左侧：活跃排名 (柱状)
  barChart = echarts.init(barChartContainer.value);
  barChart.setOption({
    ...commonChartOption,
    title: { text: '活跃排名', textStyle: { fontSize: 12, color: '#00d4ff' }, top: 0, left: 0 },
    grid: { top: '25%', bottom: '5%', left: '0%', right: '10%', containLabel: true },
    xAxis: { type: 'value', splitLine: { show: false }, axisLabel: { show: false } },
    yAxis: { type: 'category', data: ['其他', '消防', '监控', '安全'], axisLabel: { color: '#ccc', fontSize: 10 }, axisLine: {show: false}, axisTick: {show: false} },
    series: [{
      type: 'bar', data: [45, 85, 120, 200], barWidth: 8,
      itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#005bea' }, { offset: 1, color: '#00c6fb' }]), borderRadius: [0, 5, 5, 0] },
      label: { show: true, position: 'right', color: '#fff' }
    }]
  });

  // 左侧：7日报警趋势 (折线)
  lineChart = echarts.init(lineChartContainer.value);
  lineChart.setOption({
    ...commonChartOption,
    title: { text: '7日报警趋势', textStyle: { fontSize: 12, color: '#00d4ff' }, top: 0, left: 0 },
    grid: { top: '25%', bottom: '5%', left: '5%', right: '5%', containLabel: true },
    xAxis: { type: 'category', data: ['M', 'T', 'W', 'T', 'F', 'S', 'S'], boundaryGap: false, axisLabel: { color: '#aaa', fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#ffffff11' } }, axisLabel: { color: '#aaa', fontSize: 10 } },
    series: [{
      type: 'line', data: [12, 18, 9, 24, 15, 30, 21], smooth: true, symbol: 'none',
      lineStyle: { color: '#00d4ff', width: 2 },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0, 212, 255, 0.5)' }, { offset: 1, color: 'rgba(0, 212, 255, 0)' }]) }
    }]
  });

  // 右侧：分布 (环形)
  donutChart = echarts.init(donutChartContainer.value);
  donutChart.setOption({
    series: [{
      type: 'pie', radius: ['50%', '70%'], center: ['50%', '50%'],
      label: { show: false },
      data: [
        { value: 40, itemStyle: { color: '#ff4d4d' } },
        { value: 30, itemStyle: { color: '#ffd93d' } },
        { value: 20, itemStyle: { color: '#00d4ff' } },
        { value: 10, itemStyle: { color: '#a8dadc' } }
      ]
    }]
  });

  // 右侧：评分 (雷达)
  radarChart = echarts.init(radarChartContainer.value);
  radarChart.setOption({
    radar: {
      indicator: [
        { name: 'A区', max: 100 }, { name: 'B区', max: 100 }, { name: 'C区', max: 100 },
        { name: 'D区', max: 100 }, { name: 'E区', max: 100 }
      ],
      center: ['50%', '50%'], radius: '65%',
      splitArea: { show: false },
      axisName: { color: '#aaa', fontSize: 9 },
      axisLine: { lineStyle: { color: '#00d4ff55' } },
      splitLine: { lineStyle: { color: '#00d4ff33' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [85, 90, 75, 95, 80],
        itemStyle: { color: '#00d4ff' },
        areaStyle: { color: 'rgba(0, 212, 255, 0.4)' }
      }]
    }]
  });
};

const autoScrollAlarms = () => {
  const types = ['设备离线', '温度过高', '非法入侵', '未戴安全帽', '烟感异常'];
  const levels = ['high', 'medium', 'critical', 'low', 'high'];
  
  for(let i=0; i<6; i++) {
       alarmList.value.push({ 
           id: i, 
           time: '21:59:2' + i, 
           deviceId: 'DEV-'+(100+i), 
           msg: types[i%5], 
           level: levels[i%5] 
       });
  }

  alarmInterval = setInterval(() => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-GB', {hour12: false});
    const newAlarm = { 
      id: Date.now(), 
      time: timeStr, 
      deviceId: `DEV-${Math.floor(Math.random()*900)+100}`, 
      msg: types[Math.floor(Math.random()*types.length)], 
      level: levels[Math.floor(Math.random()*levels.length)]
    };
    alarmList.value.unshift(newAlarm);
    if(alarmList.value.length > 8) alarmList.value.pop();
  }, 2000);
};

const updateTime = () => {
    const now = new Date();
    timeHM.value = now.toLocaleTimeString('en-GB', { hour12: false });
    dateYMD.value = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
};

const handleResize = () => {
  [mapChart, barChart, lineChart, donutChart, radarChart].forEach(c => c && c.resize());
};

onMounted(async () => {
  updateTime();
  clockTimer = setInterval(updateTime, 1000);
  
  await nextTick();
  initMap();
  initCharts();
  autoScrollAlarms();

  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  clearInterval(clockTimer);
  clearInterval(alarmInterval);
  window.removeEventListener('resize', handleResize);
  [mapChart, barChart, lineChart, donutChart, radarChart].forEach(c => c && c.dispose());
});
</script>

<template>
  <div class="dashboard-container">
    <header class="header">
      <h1>安普物联网云平台数字中控</h1>
      <div class="header-info">
          <div class="weather-box">
              <span class="weather-icon">⛈️</span>
              <span class="weather-temp">19°C - 22°C</span>
          </div>
          <div class="time-box">
              <div class="time-hm">{{ timeHM }}</div>
              <div class="time-date">{{ dateYMD }}</div>
          </div>
      </div>
    </header>

    <div class="map-layer" ref="mapContainer" @click.self="showMapPopup = false"></div>
    
    <transition name="fade">
        <div v-if="showMapPopup" class="map-popup" :style="{ left: '50%', top: '50%' }">
            <div class="popup-header">
                {{ selectedDevice.name }} 
                <span class="close-btn" @click="showMapPopup = false">×</span>
            </div>
            <div class="popup-content">
                <div class="popup-item"><span>类型:</span> {{ selectedDevice.type }}</div>
                <div class="popup-item"><span>状态:</span> <span :style="{color: selectedDevice.status === '正常' ? '#00d4ff' : '#ff4d4d'}">{{ selectedDevice.status }}</span></div>
                <div class="popup-item"><span>温度:</span> {{ selectedDevice.temp }}</div>
            </div>
        </div>
    </transition>

    <aside class="panel left-panel">
      <div class="panel-block device-status-block">
          <div class="panel-title">设备在线状态</div>
          <div class="metric-grid">
              <div v-for="item in deviceStats" :key="item.id" class="metric-card">
                  <div class="metric-icon">{{ item.icon }}</div>
                  <div class="metric-info">
                      <div class="metric-name">{{ item.name }}</div>
                      <div class="metric-value"><span class="online">{{ item.online }}</span> / {{ item.total }}</div>
                  </div>
              </div>
          </div>
      </div>
      <div class="panel-block chart-block">
          <div class="chart-container" ref="barChartContainer"></div>
      </div>
      <div class="panel-block chart-block">
          <div class="chart-container" ref="lineChartContainer"></div>
      </div>
    </aside>

    <aside class="panel right-panel">
      <div class="panel-block alarm-stats-block">
          <div class="panel-title">今日报警统计</div>
          <div class="alarm-metrics">
              <div v-for="item in alarmStats" :key="item.name" class="alarm-metric-item">
                  <div class="alarm-icon" :style="{ color: item.color }">{{ item.icon }}</div>
                  <div class="alarm-info">
                      <div class="alarm-count" :style="{ color: item.color }">{{ item.value }}</div>
                      <div class="alarm-name">{{ item.name }}</div>
                  </div>
              </div>
          </div>
      </div>
      
      <div class="panel-block charts-row">
          <div class="chart-half">
              <div class="chart-container" ref="donutChartContainer"></div>
          </div>
          <div class="chart-half">
              <div class="chart-container" ref="radarChartContainer"></div>
          </div>
      </div>

      <div class="panel-block alarm-list-block">
        <div class="panel-title">实时报警推送</div>
        <div class="alarm-list-container">
          <transition-group name="list" tag="ul" class="alarm-ul">
            <li v-for="alarm in alarmList" :key="alarm.id" class="alarm-item" :class="alarm.level">
              <div class="alarm-time">{{ alarm.time }}</div>
              <div class="alarm-device">{{ alarm.deviceId }}</div>
              <div class="alarm-msg">{{ alarm.msg }}</div>
            </li>
          </transition-group>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
/* 确保容器能适应 DataSummary.vue 中的父盒子 */
.dashboard-container {
    --theme-blue: #00d4ff;
    --theme-bg: #050e24;
    --panel-bg: rgba(13, 27, 62, 0.75);
    --panel-border: rgba(0, 212, 255, 0.3);
    --font-number: 'Consolas', 'Monaco', monospace;

    position: relative; 
    width: 100%;  /* 改为 100% 适应父容器 */
    height: 100%; /* 改为 100% 适应父容器 */
    overflow: hidden;
    background-color: var(--theme-bg);
    /* 恢复径向渐变背景 */
    background-image: radial-gradient(circle at center, #0a1a33 0%, #050e24 100%);
    font-family: 'Segoe UI', Roboto, sans-serif; 
    color: #fff;
    box-sizing: border-box;
}

/* 顶部 Header */
.header {
  position: absolute; top: 0; left: 0; width: 100%; height: 60px; z-index: 20;
  display: flex; justify-content: center; align-items: center; pointer-events: none;
  background: linear-gradient(to bottom, rgba(10, 26, 60, 0.95), transparent);
  border-bottom: 1px solid rgba(0,212,255,0.1);
}

.header h1 {
  font-size: 22px; margin: 0; letter-spacing: 3px; color: var(--theme-blue);
  text-shadow: 0 0 10px var(--theme-blue); font-weight: bold; pointer-events: auto;
}

.header-info {
    position: absolute; right: 20px; top: 0; height: 60px;
    display: flex; align-items: center; gap: 20px; pointer-events: auto;
}
.weather-box { display: flex; align-items: center; gap: 8px; color: var(--theme-blue); font-size: 13px; }
.time-box { text-align: right; }
.time-hm { font-size: 18px; font-weight: bold; font-family: var(--font-number); color: #fff; }
.time-date { font-size: 12px; color: #aaa; }

/* 地图层 */
.map-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
.map-popup {
    position: absolute; width: 240px; padding: 10px; z-index: 30;
    background: rgba(13, 27, 62, 0.9); border: 1px solid var(--theme-blue);
    border-radius: 4px; transform: translate(-50%, -50%); backdrop-filter: blur(5px);
}
.popup-header { color: var(--theme-blue); border-bottom: 1px solid rgba(0,212,255,0.2); margin-bottom: 5px; font-weight: bold;}
.close-btn { float: right; cursor: pointer; }

/* 左右面板通用 */
.panel {
  position: absolute; top: 60px; bottom: 10px; width: 28%; z-index: 10;
  display: flex; flex-direction: column; gap: 10px; pointer-events: none; 
}
.left-panel { left: 10px; }
.right-panel { right: 10px; }

/* 面板内部卡片 - 科技感边框 */
.panel-block {
    background: var(--panel-bg); backdrop-filter: blur(10px);
    border: 1px solid var(--panel-border); 
    box-shadow: inset 0 0 10px rgba(0,212,255,0.1);
    border-radius: 4px; padding: 10px; display: flex; flex-direction: column;
    position: relative; overflow: hidden; pointer-events: auto;
}
/* 装饰角标 */
.panel-block::before { content: ''; position: absolute; top: 0; left: 0; width: 10px; height: 10px; border-top: 2px solid var(--theme-blue); border-left: 2px solid var(--theme-blue); }
.panel-block::after { content: ''; position: absolute; bottom: 0; right: 0; width: 10px; height: 10px; border-bottom: 2px solid var(--theme-blue); border-right: 2px solid var(--theme-blue); }

.panel-title { font-size: 14px; font-weight: bold; margin-bottom: 8px; color: var(--theme-blue); display: flex; align-items: center; }
.panel-title::before { content: ''; display: inline-block; width: 4px; height: 12px; background: var(--theme-blue); margin-right: 6px; }

/* 左侧内容 */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.metric-card { display: flex; align-items: center; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 4px; }
.metric-icon { font-size: 20px; margin-right: 8px; }
.metric-name { font-size: 12px; color: #aaa; }
.metric-value { font-size: 12px; font-family: var(--font-number); }
.metric-value .online { color: var(--theme-blue); font-size: 14px; font-weight: bold; }
.chart-block { flex: 1; min-height: 0; }
.chart-container { width: 100%; height: 100%; }

/* 右侧内容 */
.alarm-metrics { display: flex; justify-content: space-around; margin-bottom: 5px; }
.alarm-metric-item { text-align: center; }
.alarm-icon { font-size: 18px; margin-bottom: 2px; }
.alarm-count { font-size: 16px; font-weight: bold; font-family: var(--font-number); }
.alarm-name { font-size: 12px; color: #aaa; }

.charts-row { height: 160px; flex-direction: row; gap: 5px; }
.chart-half { flex: 1; height: 100%; position: relative; }

.alarm-list-block { flex: 1.5; overflow: hidden; }
.alarm-list-container { flex: 1; overflow: hidden; position: relative; }
.alarm-ul { list-style: none; padding: 0; margin: 0; }
.alarm-item { display: flex; align-items: center; padding: 6px; margin-bottom: 5px; background: rgba(0, 0, 0, 0.3); border-left: 2px solid; border-radius: 2px; font-size: 12px; }
.alarm-item.high { border-color: #ff4d4d; background: rgba(255, 77, 77, 0.1); }
.alarm-item.critical { border-color: #ff0000; background: rgba(255, 0, 0, 0.2); animation: flash 1.5s infinite; }
.alarm-item.medium { border-color: #ffd93d; background: rgba(255, 217, 61, 0.1); }
.alarm-item.low { border-color: var(--theme-blue); background: rgba(0, 212, 255, 0.1); }
.alarm-time { color: #aaa; margin-right: 8px; width: 60px; font-family: var(--font-number); }
.alarm-device { color: var(--theme-blue); margin-right: 8px; width: 60px; }
.alarm-msg { color: #fff; flex: 1; }

@keyframes flash { 0%, 100% { box-shadow: inset 0 0 0 red; } 50% { box-shadow: inset 0 0 10px rgba(255,0,0,0.5); } }
.list-enter-active, .list-leave-active { transition: all 0.5s ease; }
.list-enter-from { opacity: 0; transform: translateX(20px); }
.list-leave-to { opacity: 0; transform: translateX(-20px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>