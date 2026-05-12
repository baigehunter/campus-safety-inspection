<template>
  <view class="page">
    <!-- Profile Header -->
    <view class="profile-header">
      <view class="header-bg">
        <view class="header-geo header-geo--1"></view>
        <view class="header-geo header-geo--2"></view>
      </view>
      <view class="header-content">
        <view class="avatar-wrap" :class="{ 'anim-scale-in': pageReady }">
          <view class="avatar">
            <text class="avatar-text">{{ initial }}</text>
          </view>
          <view class="avatar-ring"></view>
        </view>
        <view class="profile-info" :class="{ 'anim-fade-up delay-1': pageReady }">
          <text class="profile-name">{{ userInfo.username || '巡检员' }}</text>
          <view class="profile-role">
            <view class="role-dot"></view>
            <text>{{ userInfo.role_name || userInfo.role || '巡检员' }}</text>
          </view>
        </view>
      </view>
      <!-- Header bottom curve -->
      <view class="header-curve"></view>
    </view>

    <!-- Stats Row -->
    <view class="stats-row">
      <view
        class="stat-card"
        :class="{ 'anim-fade-up delay-1': pageReady }"
        v-for="(stat, idx) in stats"
        :key="stat.key"
      >
        <text class="stat-value">{{ stat.value }}</text>
        <text class="stat-label">{{ stat.label }}</text>
      </view>
    </view>

    <!-- Menu Sections -->
    <view class="menu-section">
      <!-- User Info -->
      <view class="menu-group" :class="{ 'anim-fade-up delay-1': pageReady }">
        <view class="menu-group-label">
          <text>注册信息</text>
        </view>
        <view class="menu-card info-card">
          <view class="info-row">
            <view class="info-left">
              <text class="info-label">用户名</text>
            </view>
            <text class="info-value">{{ userInfo.username || '未填写' }}</text>
          </view>
          <view class="menu-divider"></view>
          <view class="info-row">
            <view class="info-left">
              <text class="info-label">邮箱</text>
            </view>
            <text class="info-value" :class="{ 'info-value--empty': !userInfo.email }">{{ userInfo.email || '未填写' }}</text>
          </view>
          <view class="menu-divider"></view>
          <view class="info-row">
            <view class="info-left">
              <text class="info-label">手机号</text>
            </view>
            <text class="info-value" :class="{ 'info-value--empty': !userInfo.phone }">{{ userInfo.phone || '未填写' }}</text>
          </view>
          <view class="menu-divider"></view>
          <view class="info-row">
            <view class="info-left">
              <text class="info-label">角色</text>
            </view>
            <text class="info-value">{{ userInfo.role_name || '未设置' }}</text>
          </view>
          <view class="menu-divider"></view>
          <view class="info-row">
            <view class="info-left">
              <text class="info-label">注册时间</text>
            </view>
            <text class="info-value">{{ formatDate(userInfo.date_joined) || '未知' }}</text>
          </view>
        </view>
      </view>

      <!-- Notification Settings -->
      <view class="menu-group" :class="{ 'anim-fade-up delay-3': pageReady }">
        <view class="menu-group-label">
          <text>通知设置</text>
        </view>
        <view class="menu-card">
          <view class="menu-item btn-press" @click="openSubscribe">
            <view class="menu-left">
              <view class="menu-icon menu-icon--cyan">
                <text class="menu-icon-text">@</text>
              </view>
              <view class="menu-body">
                <text class="menu-label">消息订阅</text>
                <text class="menu-hint">接收巡检异常、整改任务等重要通知</text>
              </view>
            </view>
            <view class="menu-right">
              <text class="menu-arrow">&rsaquo;</text>
            </view>
          </view>
          <view class="menu-divider"></view>
          <view class="menu-item btn-press" @click="goToNotifications">
            <view class="menu-left">
              <view class="menu-icon menu-icon--indigo">
                <text class="menu-icon-text">%</text>
              </view>
              <view class="menu-body">
                <text class="menu-label">消息中心</text>
                <text class="menu-hint">查看所有通知和历史消息</text>
              </view>
            </view>
            <view class="menu-right">
              <view class="menu-badge" v-if="unreadCount > 0">
                <text>{{ unreadCount > 99 ? '99+' : unreadCount }}</text>
              </view>
              <text class="menu-arrow">&rsaquo;</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Account -->
      <view class="menu-group" :class="{ 'anim-fade-up delay-4': pageReady }">
        <view class="menu-group-label">
          <text>账户</text>
        </view>
        <view class="menu-card">
          <view class="menu-item btn-press" @click="handleLogout">
            <view class="menu-left">
              <view class="menu-icon menu-icon--danger">
                <text class="menu-icon-text">+</text>
              </view>
              <view class="menu-body">
                <text class="menu-label menu-label--danger">退出登录</text>
                <text class="menu-hint">退出当前账号并返回登录页</text>
              </view>
            </view>
            <view class="menu-right">
              <text class="menu-arrow">&rsaquo;</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Version -->
    <view class="version" :class="{ 'anim-fade-up delay-5': pageReady }">
      <text>校园安全巡检 v1.0.0</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '@/utils/request'
import { requestSubscribe } from '@/utils/subscribe'

const userInfo = ref<any>({})
const stats = ref([
  { key: 'inspection', value: 0, label: '巡检次数' },
  { key: 'hazard', value: 0, label: '上报隐患' },
  { key: 'task', value: 0, label: '整改完成' }
])
const unreadCount = ref(0)
const pageReady = ref(false)

const initial = computed(() => {
  const name = userInfo.value?.username || '巡'
  return name.charAt(0).toUpperCase()
})

onMounted(() => {
  userInfo.value = uni.getStorageSync('userInfo') || {}
  loadData()
})

onShow(() => {
  pageReady.value = false
  nextTick(() => { pageReady.value = true })
  loadData()
})

async function loadData() {
  try {
    const res: any = await api.getUserInfo()
    if (res && res.username) userInfo.value = res
  } catch {
    userInfo.value = uni.getStorageSync('userInfo') || {}
  }

  // 三个计数分别查，目前后端没有汇总接口所以只能这样。
  // page_size=1 只拿 metadata 里的 count，不拉实际数据
  try {
    const [recordsRes, hazardsRes, tasksRes] = await Promise.all([
      api.getRecords({ page_size: 1 }),
      api.getHazards({ page_size: 1 }),
      api.getTasks({ status: 'completed', page_size: 1 })
    ])
    stats.value[0].value = (recordsRes as any).count || 0
    stats.value[1].value = (hazardsRes as any).count || 0
    stats.value[2].value = (tasksRes as any).count || 0
  } catch {
    // 统计数加载失败也不影响页面，保持 0 就行了
  }

  try {
    const unreadRes: any = await api.getUnreadCount()
    unreadCount.value = unreadRes.total_unread || 0
  } catch {
    // 同上，静默失败
  }

  nextTick(() => { pageReady.value = true })
}

function openSubscribe() {
  requestSubscribe(['hazard_new', 'hazard_assigned', 'rectify_result', 'inspection_overdue', 'ai_abnormal'])
}

function goToNotifications() {
  uni.navigateTo({ url: '/pages/notifications/index' })
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出当前账号吗？',
    confirmColor: '#ef4444',
    success: async (res) => {
      if (res.confirm) {
        try {
          const refreshToken = uni.getStorageSync('refresh_token')
          // 调后端登出接口，把 refresh token 拉黑。
          // 失败了也无所谓——反正前端会把本地 token 清掉
          if (refreshToken) await api.logout(refreshToken)
        } catch {
          // 登出接口调用失败不影响退出
        } finally {
          uni.removeStorageSync('access_token')
          uni.removeStorageSync('refresh_token')
          uni.removeStorageSync('userInfo')
          uni.reLaunch({ url: '/pages/login/index' })
        }
      }
    }
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-primary);
  padding-bottom: 140rpx;
}

/* ==============================
   HEADER
   ============================== */
.profile-header {
  position: relative;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(165deg, #0a1228 0%, #0f2d54 35%, #084c5c 100%);
}

.header-geo {
  position: absolute;
  border: 2rpx solid rgba(6, 182, 212, 0.08);
  border-radius: 32rpx;
}

.header-geo--1 {
  top: -40rpx;
  right: -20rpx;
  width: 200rpx;
  height: 200rpx;
  transform: rotate(30deg);
}

.header-geo--2 {
  bottom: -50rpx;
  left: -30rpx;
  width: 160rpx;
  height: 160rpx;
  transform: rotate(-15deg);
  border-color: rgba(255, 255, 255, 0.06);
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 32rpx 56rpx;
}

.header-curve {
  position: relative;
  z-index: 1;
  height: 48rpx;
  background: var(--color-bg-primary);
  border-radius: 40rpx 40rpx 0 0;
  margin-top: -1rpx;
}

/* Avatar */
.avatar-wrap {
  position: relative;
  margin-bottom: 24rpx;
}

.avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  border: 3rpx solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-ring {
  position: absolute;
  inset: -6rpx;
  border-radius: 50%;
  border: 2rpx solid rgba(6, 182, 212, 0.2);
}

.avatar-text {
  font-size: 56rpx;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 2rpx;
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.profile-name {
  font-size: 38rpx;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 1rpx;
}

.profile-role {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(255, 255, 255, 0.1);
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.75);
}

.role-dot {
  width: 8rpx;
  height: 8rpx;
  background: #22d3ee;
  border-radius: 50%;
}

/* ==============================
   STATS ROW
   ============================== */
.stats-row {
  display: flex;
  gap: 16rpx;
  padding: 0 32rpx;
  margin-top: -20rpx;
  position: relative;
  z-index: 2;
}

.stat-card {
  flex: 1;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 28rpx 20rpx;
  text-align: center;
  box-shadow: var(--shadow-md);
}

.stat-value {
  display: block;
  font-size: 44rpx;
  font-weight: 800;
  color: var(--color-brand-900);
  line-height: 1.1;
  margin-bottom: 6rpx;
}

.stat-label {
  font-size: 26rpx;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* ==============================
   MENU SECTIONS
   ============================== */
.menu-section {
  padding: 32rpx 32rpx 0;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.menu-group-label {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 14rpx;
  padding-left: 4rpx;
  text-transform: uppercase;
  letter-spacing: 2rpx;
}

.menu-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 24rpx;
  min-height: 100rpx;
}

.menu-item:active {
  background: var(--color-bg-secondary);
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
  flex: 1;
  min-width: 0;
}

.menu-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon--cyan { background: rgba(6, 182, 212, 0.1); }
.menu-icon--indigo { background: rgba(99, 102, 241, 0.1); }
.menu-icon--danger { background: rgba(239, 68, 68, 0.08); }

.menu-icon-text {
  font-size: 32rpx;
  font-weight: 700;
}

.menu-icon--cyan .menu-icon-text { color: #06b6d4; }
.menu-icon--indigo .menu-icon-text { color: #6366f1; }
.menu-icon--danger .menu-icon-text { color: #ef4444; transform: rotate(45deg); }

.menu-body {
  flex: 1;
  min-width: 0;
}

.menu-label {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4rpx;
}

.menu-label--danger {
  color: #ef4444;
}

.menu-hint {
  font-size: 28rpx;
  color: var(--color-text-secondary);
}

.menu-right {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-shrink: 0;
}

.menu-badge {
  min-width: 36rpx;
  height: 36rpx;
  background: #ef4444;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
}

.menu-badge text {
  font-size: 28rpx;
  font-weight: 600;
  color: #ffffff;
}

.menu-arrow {
  font-size: 36rpx;
  color: #cbd5e1;
}

.menu-divider {
  height: 1rpx;
  background: var(--color-border-light);
  margin: 0 24rpx;
}

/* Info Card */
.info-card {
  padding: 8rpx 0;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  min-height: 88rpx;
}

.info-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.info-label {
  font-size: 30rpx;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.info-value {
  font-size: 30rpx;
  color: var(--color-text-primary);
  font-weight: 600;
}

.info-value--empty {
  color: #94a3b8;
  font-weight: 400;
}

/* ==============================
   VERSION
   ============================== */
.version {
  text-align: center;
  padding: 48rpx 32rpx;
  font-size: 28rpx;
  color: var(--color-text-secondary);
}
</style>
