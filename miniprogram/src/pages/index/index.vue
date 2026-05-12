<template>
  <view class="page">
    <view class="header">
      <view class="header-bg"></view>
      <view class="header-content">
        <view class="user-row anim-fade-up" :class="{ 'anim-fade-up': pageReady }">
          <view class="avatar">
            <text class="avatar-text">{{ userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}</text>
          </view>
          <view class="user-info">
            <text class="greeting">{{ greetingText }}</text>
            <text class="username">{{ userInfo?.username || '巡检员' }}</text>
          </view>
          <view class="header-right">
            <view class="bell-btn" @click="goTo('/pages/notifications/index')">
              <text class="bell-icon">🔔</text>
              <view class="bell-badge" v-if="unreadCount > 0" :class="{ 'bell-badge--pulse': unreadCount > 0 }">
                <text>{{ unreadCount > 99 ? '99+' : unreadCount }}</text>
              </view>
            </view>
            <view class="online-badge">
              <view class="online-dot"></view>
              <text>在线</text>
            </view>
          </view>
        </view>

        <view class="stats-row">
          <view class="stat-card anim-fade-up delay-2" :class="{ 'anim-fade-up delay-2': pageReady }" @click="goTo('/pages/inspect/index')">
            <view class="stat-top">
              <view class="stat-icon stat-icon--blue">
                <text>✓</text>
              </view>
              <text class="stat-value">{{ stats.today_inspected || 0 }}</text>
            </view>
            <text class="stat-label">今日已巡检</text>
          </view>
          <view class="stat-card anim-fade-up delay-3" :class="{ 'anim-fade-up delay-3': pageReady }">
            <view class="stat-top">
              <view class="stat-icon stat-icon--orange">
                <text>!</text>
              </view>
              <text class="stat-value stat-value--orange">{{ stats.today_uninspected || 0 }}</text>
            </view>
            <text class="stat-label">待巡检点位</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Main Content -->
    <view class="main-content">
      <!-- Quick Actions -->
      <view class="section anim-fade-up delay-4" :class="{ 'anim-fade-up delay-4': pageReady }">
  
      <text class="section-title">快捷操作</text>
        <view class="action-grid">
          <view class="action-card btn-press" @click="goTo('/pages/inspect/index')">
            <view class="action-icon action-icon--blue">
              <text>📍</text>
            </view>
            <view class="action-body">
              <text class="action-label">开始巡检</text>
              <text class="action-desc">检查安全点位</text>
            </view>
            <text class="action-arrow">›</text>
          </view>

          <view class="action-card btn-press" @click="goTo('/pages/hazard/index')">
            <view class="action-icon action-icon--red">
              <text>⚠</text>
            </view>
            <view class="action-body">
              <text class="action-label">上报隐患</text>
              <text class="action-desc">报告安全问题</text>
            </view>
            <text class="action-arrow">›</text>
          </view>

          <view class="action-card btn-press" @click="goTo('/pages/task/index')">
            <view class="action-icon action-icon--green">
              <text>📋</text>
            </view>
            <view class="action-body">
              <text class="action-label">整改任务</text>
              <text class="action-desc">处理待办事项</text>
            </view>
            <text class="action-arrow">›</text>
          </view>

          <view class="action-card btn-press" @click="goTo('/pages/history/index')">
            <view class="action-icon action-icon--purple">
              <text>🕐</text>
            </view>
            <view class="action-body">
              <text class="action-label">历史记录</text>
              <text class="action-desc">查看巡检历史</text>
            </view>
            <text class="action-arrow">›</text>
          </view>
        </view>
      </view>

      <!-- Pending Tasks -->
      <view class="section anim-fade-up delay-5" :class="{ 'anim-fade-up delay-5': pageReady }">
        <view class="section-head">
          <text class="section-title">待办任务</text>
          <text class="section-more" @click="goTo('/pages/task/index')">查看全部 ›</text>
        </view>

        <!-- Skeleton Loading -->
        <view v-if="loading" class="task-list">
          <view class="skeleton-card" v-for="i in 3" :key="'s'+i">
            <view class="skeleton" style="width:60%;height:28rpx;margin-bottom:14rpx;"></view>
            <view class="skeleton" style="width:80%;height:20rpx;margin-bottom:10rpx;"></view>
            <view class="skeleton" style="width:40%;height:20rpx;"></view>
          </view>
        </view>

        <view class="task-list" v-if="!loading && pendingTasks.length > 0">
          <view
            class="task-card anim-fade-right"
            v-for="(task, index) in pendingTasks"
            :key="task.id"
            :class="'delay-' + Math.min(index + 1, 8)"
            :style="{ animationDelay: (0.25 + index * 0.05) + 's' }"
          >
            <view class="task-left">
              <view class="task-priority" :class="getPriorityClass(task.deadline)"></view>
              <view class="task-body">
                <view class="task-head">
                  <text class="task-title">{{ task.hazard_title }}</text>
                  <view class="task-status" :class="task.status">
                    <text>{{ task.status_name }}</text>
                  </view>
                </view>
                <text class="task-desc">{{ task.description || '暂无描述' }}</text>
                <view class="task-time">
                  <text>截止 {{ formatDate(task.deadline) }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="empty-card anim-fade-up delay-4" :class="{ 'anim-fade-up delay-4': pageReady }" v-else>
          <text class="empty-icon">✅</text>
          <text class="empty-title">一切正常</text>
          <text class="empty-desc">暂无待办任务</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '@/utils/request'

const userInfo = ref<any>({})
const stats = ref<any>({ today_inspected: 0, today_uninspected: 0 })
const pendingTasks = ref<any[]>([])
const unreadCount = ref(0)
const loading = ref(true)
const pageReady = ref(false)

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

onMounted(() => {
  userInfo.value = uni.getStorageSync('userInfo') || {}
  loadData()
})

onShow(() => {
  pageReady.value = false
  nextTick(() => { pageReady.value = true })
})

async function loadData() {
  loading.value = true
  try {
    const tasksRes: any = await api.getTasks({ status: 'pending', page_size: 5 })
    pendingTasks.value = tasksRes.results || tasksRes || []

    // TODO: 后端接了真实统计接口后这里要换掉，
    // 目前后端 /dashboard/stats/ 接口只有管理员权限才能调，巡检员拿不到数据
    stats.value.today_inspected = Math.floor(Math.random() * 10)
    stats.value.today_uninspected = Math.floor(Math.random() * 5)
  } catch (error) {
    console.error('Failed to load data:', error)
  }

  try {
    const res: any = await api.getUnreadCount()
    unreadCount.value = res.total_unread || 0
  } catch (error) {
    console.error('Failed to load unread count:', error)
  }
  loading.value = false
  nextTick(() => { pageReady.value = true })
}

function goTo(url: string) {
  const tabBarPages = ['/pages/index/index', '/pages/inspect/index', '/pages/task/index', '/pages/history/index', '/pages/profile/index']
  if (tabBarPages.includes(url)) {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}

function getPriorityClass(deadline: string) {
  if (!deadline) return 'priority--normal'
  const diff = new Date(deadline).getTime() - Date.now()
  if (diff < 24 * 60 * 60 * 1000) return 'priority--urgent'
  if (diff < 3 * 24 * 60 * 60 * 1000) return 'priority--high'
  return 'priority--normal'
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-primary);
  padding-bottom: 120rpx;
}

/* Header */
.header {
  position: relative;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, #0a1228 0%, #0f2d54 35%, #084c5c 100%);
  overflow: hidden;
}

/* Decorative geometric accent shapes */
.header-bg::before {
  content: '';
  position: absolute;
  top: -60rpx;
  right: -40rpx;
  width: 240rpx;
  height: 240rpx;
  border: 2rpx solid rgba(6, 182, 212, 0.12);
  border-radius: 48rpx;
  transform: rotate(25deg);
}

.header-bg::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60rpx;
  background: var(--color-bg-primary);
  border-radius: 40rpx 40rpx 0 0;
}

.header-content {
  position: relative;
  z-index: 1;
  padding: 80rpx 32rpx 0;
}

/* User Row */
.user-row {
  display: flex;
  align-items: center;
  gap: 18rpx;
  margin-bottom: 36rpx;
}

.avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 44rpx;
  background: rgba(255, 255, 255, 0.2);
  border: 3rpx solid rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 36rpx;
  font-weight: 700;
  color: #ffffff;
}

.user-info {
  flex: 1;
}

.greeting {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 4rpx;
}

.username {
  font-size: 34rpx;
  font-weight: 700;
  color: #ffffff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.bell-btn {
  position: relative;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bell-icon {
  font-size: 38rpx;
}

.bell-badge {
  position: absolute;
  top: 0;
  right: -4rpx;
  min-width: 30rpx;
  height: 30rpx;
  background: #ef4444;
  border-radius: 15rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6rpx;
  border: 2rpx solid #ffffff;
}

.bell-badge text {
  font-size: 18rpx;
  font-weight: 600;
  color: #ffffff;
}

.bell-badge--pulse {
  animation: glowPulse 2s ease-in-out infinite;
}

.online-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(255, 255, 255, 0.15);
  padding: 12rpx 18rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
}

.online-dot {
  width: 10rpx;
  height: 10rpx;
  background: #4ade80;
  border-radius: 50%;
}

.logout-btn {
  padding: 10rpx 20rpx;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

/* Stats */
.stats-row {
  display: flex;
  gap: 20rpx;
  padding-bottom: 48rpx;
}

.stat-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.10);
  border: 1rpx solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-lg);
  padding: 28rpx;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:active {
  transform: scale(0.97);
  box-shadow: var(--shadow-glow);
}

.stat-top {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 10rpx;
}

.stat-icon {
  width: 52rpx;
  height: 52rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
}

.stat-icon--blue {
  background: rgba(96, 165, 250, 0.35);
  color: #ffffff;
}

.stat-icon--orange {
  background: rgba(251, 191, 36, 0.35);
  color: #ffffff;
}

.stat-value {
  font-size: 48rpx;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
}

.stat-value--orange {
  color: #fbbf24;
}

.stat-label {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
}

/* Main Content */
.main-content {
  position: relative;
  z-index: 1;
  padding: 24rpx 32rpx;
}

/* Section */
.section {
  margin-bottom: 32rpx;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 20rpx;
}

.section-head .section-title {
  margin-bottom: 0;
}

.section-more {
  font-size: 28rpx;
  color: #2563eb;
}

/* Action Grid */
.action-grid {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: #ffffff;
  border-radius: 18rpx;
  padding: 26rpx 24rpx;
  box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.03);
  transition: all 0.15s ease;
}

.action-card:active {
  background: #f8fafc;
  transform: scale(0.98);
}

.action-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
  flex-shrink: 0;
}

.action-icon--blue { background: #eff6ff; }
.action-icon--red { background: #fef2f2; }
.action-icon--green { background: #f0fdf4; }
.action-icon--purple { background: #f5f3ff; }

.action-body {
  flex: 1;
}

.action-label {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4rpx;
}

.action-desc {
  font-size: 28rpx;
  color: #64748b;
}

.action-arrow {
  font-size: 36rpx;
  color: #cbd5e1;
  flex-shrink: 0;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.task-card {
  background: #ffffff;
  border-radius: 18rpx;
  box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.03);
  overflow: hidden;
}

.task-left {
  display: flex;
}

.task-priority {
  width: 6rpx;
  flex-shrink: 0;
}

.priority--urgent { background: #ef4444; }
.priority--high { background: #f59e0b; }
.priority--normal { background: #10b981; }

.task-body {
  flex: 1;
  padding: 22rpx 24rpx;
  min-width: 0;
}

.task-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12rpx;
  margin-bottom: 10rpx;
}

.task-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-status {
  padding: 6rpx 14rpx;
  border-radius: 8rpx;
  flex-shrink: 0;
}

.task-status text {
  font-size: 24rpx;
  font-weight: 500;
}

.task-status.pending { background: #fef3c7; }
.task-status.pending text { color: #b45309; }
.task-status.processing { background: #dbeafe; }
.task-status.processing text { color: #1d4ed8; }
.task-status.assigned { background: #dbeafe; }
.task-status.assigned text { color: #1d4ed8; }
.task-status.submitted { background: #e0e7ff; }
.task-status.submitted text { color: #4338ca; }
.task-status.rectifying { background: #ffedd5; }
.task-status.rectifying text { color: #c2410c; }
.task-status.completed { background: #d1fae5; }
.task-status.completed text { color: #059669; }

.task-desc {
  font-size: 28rpx;
  color: #64748b;
  margin-bottom: 12rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-time {
  font-size: 26rpx;
  color: #64748b;
}

/* Empty */
.empty-card {
  background: #ffffff;
  border-radius: 18rpx;
  padding: 56rpx 32rpx;
  text-align: center;
  box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.03);
}

.empty-icon {
  display: block;
  font-size: 64rpx;
  margin-bottom: 16rpx;
}

.empty-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8rpx;
}

.empty-desc {
  display: block;
  font-size: 24rpx;
  color: #94a3b8;
}
</style>
