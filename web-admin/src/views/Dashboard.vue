<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { getDashboardStats, getChartData } from '../api'
import * as echarts from 'echarts'

const stats = ref({})
const chartData = ref({})
const loading = ref(true)

// ECharts instances
let trendChartInstance = null
let typeChartInstance = null
let areaChartInstance = null

// DOM refs
const trendChartRef = ref(null)
const typeChartRef = ref(null)
const areaChartRef = ref(null)

onMounted(async () => {
  try {
    const [statsRes, chartRes] = await Promise.all([
      getDashboardStats(),
      getChartData()
    ])
    stats.value = statsRes.data
    chartData.value = chartRes.data
    await nextTick()
    initCharts()
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (trendChartInstance) trendChartInstance.dispose()
  if (typeChartInstance) typeChartInstance.dispose()
  if (areaChartInstance) areaChartInstance.dispose()
  window.removeEventListener('resize', handleResize)
})

function initCharts() {
  // Trend Chart
  if (trendChartRef.value) {
    trendChartInstance = echarts.init(trendChartRef.value)
    trendChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: '#fff', fontFamily: 'Plus Jakarta Sans' }
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: chartData.value.trend?.map(i => i.date.slice(5)) || [],
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#64748b', fontFamily: 'Inter' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f1f5f9' } },
        axisLabel: { color: '#64748b', fontFamily: 'Inter' }
      },
      series: [{
        data: chartData.value.trend?.map(i => i.count) || [],
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#06b6d4' },
        itemStyle: { color: '#06b6d4', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(6, 182, 212, 0.25)' },
            { offset: 1, color: 'rgba(6, 182, 212, 0.02)' }
          ])
        }
      }]
    })
  }

  // Type Chart
  if (typeChartRef.value) {
    typeChartInstance = echarts.init(typeChartRef.value)
    const colors = ['#06b6d4', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#3b82f6']
    typeChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: '#fff', fontFamily: 'Plus Jakarta Sans' }
      },
      legend: {
        bottom: '5%',
        left: 'center',
        textStyle: { color: '#64748b', fontFamily: 'Inter' }
      },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold', fontFamily: 'Plus Jakarta Sans' }
        },
        data: (chartData.value.hazard_types || []).map((i, idx) => ({
          value: i.count,
          name: i.type,
          itemStyle: { color: colors[idx % colors.length] }
        }))
      }]
    })
  }

  // Area Chart
  if (areaChartRef.value) {
    areaChartInstance = echarts.init(areaChartRef.value)
    areaChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: '#fff', fontFamily: 'Plus Jakarta Sans' }
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: chartData.value.area_hazards?.map(i => i.area) || [],
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#64748b', fontFamily: 'Inter', rotate: 30 }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f1f5f9' } },
        axisLabel: { color: '#64748b', fontFamily: 'Inter' }
      },
      series: [{
        data: chartData.value.area_hazards?.map(i => i.count) || [],
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#06b6d4' },
            { offset: 1, color: '#0891b2' }
          ])
        }
      }]
    })
  }

  window.addEventListener('resize', handleResize)
}

function handleResize() {
  trendChartInstance?.resize()
  typeChartInstance?.resize()
  areaChartInstance?.resize()
}

const statCards = [
  { label: '今日已巡检', key: 'today_inspected', icon: 'check-circle', trend: 'up', color: 'cyan' },
  { label: '今日未巡检', key: 'today_uninspected', icon: 'clock', trend: 'neutral', color: 'orange' },
  { label: '新增隐患', key: 'new_hazards', icon: 'alert-triangle', trend: 'up', color: 'red' },
  { label: '已整改', key: 'rectified_hazards', icon: 'check-square', trend: 'up', color: 'green' },
  { label: '待处理隐患', key: 'pending_hazards', icon: 'file-question', trend: 'neutral', color: 'purple' },
  { label: '逾期隐患', key: 'overdue_hazards', icon: 'alert-circle', trend: 'down', color: 'red' }
]
</script>

<template>
  <div class="dashboard" v-loading="loading">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">数据监控中心</h1>
        <p class="page-subtitle">实时掌握校园安全动态</p>
      </div>
      <div class="header-actions">
        <button class="action-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span>刷新数据</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div
        v-for="(card, index) in statCards"
        :key="card.key"
        class="stat-card"
        :class="[`stat-card--${card.color}`]"
        :style="{ '--delay': `${index * 100}ms` }"
      >
        <div class="stat-icon">
          <component :is="card.icon" v-if="false" />
          <svg v-if="card.icon === 'check-circle'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <svg v-else-if="card.icon === 'clock'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <svg v-else-if="card.icon === 'alert-triangle'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <svg v-else-if="card.icon === 'check-square'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 11 12 14 22 4"/>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
          <svg v-else-if="card.icon === 'file-question'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <circle cx="12" cy="15" r="1"/>
            <path d="M10 9.5c0-.83.67-1.5 1.5-1.5h1c.83 0 1.5.67 1.5 1.5 0 .63-.4 1.17-.97 1.4-.53.21-.9.72-.9 1.35v.25"/>
          </svg>
          <svg v-else-if="card.icon === 'alert-circle'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats[card.key] || 0 }}</span>
          <span class="stat-label">{{ card.label }}</span>
        </div>
        <div class="stat-decoration"></div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="charts-row">
        <!-- Trend Chart -->
        <div class="chart-card chart-card--large">
          <div class="chart-header">
            <h3 class="chart-title">巡检趋势</h3>
            <span class="chart-period">近7天</span>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>

        <!-- Type Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">隐患类型分布</h3>
          </div>
          <div ref="typeChartRef" class="chart-container"></div>
        </div>
      </div>

      <div class="chart-card chart-card--full">
        <div class="chart-header">
          <h3 class="chart-title">各区域隐患统计</h3>
        </div>
        <div ref="areaChartRef" class="chart-container chart-container--tall"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ========================================
   Dashboard Container
   ======================================== */
.dashboard {
  padding: 0;
  min-height: 100%;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1e293b;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

/* ========================================
   Stats Cards
   ======================================== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  position: relative;
  padding: 24px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out backwards;
  animation-delay: var(--delay);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-card--cyan .stat-icon { background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); }
.stat-card--cyan .stat-decoration { background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, transparent 100%); }

.stat-card--orange .stat-icon { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.stat-card--orange .stat-decoration { background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, transparent 100%); }

.stat-card--red .stat-icon { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
.stat-card--red .stat-decoration { background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, transparent 100%); }

.stat-card--green .stat-icon { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.stat-card--green .stat-decoration { background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, transparent 100%); }

.stat-card--purple .stat-icon { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
.stat-card--purple .stat-decoration { background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%); }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.stat-decoration {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 100px;
  height: 100px;
  border-radius: 100px 0 0 0;
}

/* ========================================
   Charts Section
   ======================================== */
.charts-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}

.chart-card--large {
  grid-column: span 1;
}

.chart-card--full {
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.chart-period {
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 20px;
}

.chart-container {
  height: 280px;
  width: 100%;
}

.chart-container--tall {
  height: 320px;
}
</style>
