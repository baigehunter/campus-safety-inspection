<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">消息中心</text>
      <text class="page-subtitle">{{ unreadCount > 0 ? `${unreadCount} 条未读` : '全部已读' }}</text>
      <view class="header-actions">
        <view class="mark-all-btn" v-if="unreadCount > 0" @click="markAllRead">
          <text>全部已读</text>
        </view>
      </view>
    </view>

    <view class="filter-scroll">
      <view
        class="filter-tag"
        :class="{ active: currentFilter === '' }"
        @click="filterBy('')"
      >
        <text>全部</text>
      </view>
      <view
        class="filter-tag"
        :class="{ active: currentFilter === 'unread' }"
        @click="filterBy('unread')"
      >
        <text>未读</text>
        <text class="filter-count" v-if="unreadCount > 0">{{ unreadCount }}</text>
      </view>
      <view
        class="filter-tag"
        v-for="cat in categoryFilters"
        :key="cat.value"
        :class="{ active: currentFilter === cat.value }"
        @click="filterBy(cat.value)"
      >
        <text>{{ cat.label }}</text>
      </view>
    </view>

    <view class="list-section">
      <view class="list" v-if="notifications.length > 0">
        <view
          class="notif-card anim-fade-right"
          v-for="(item, index) in notifications"
          :key="item.id"
          :class="['delay-' + Math.min(index + 1, 8), { 'notif--unread': !item.is_read }]"
          @click="handleClick(item)"
        >
          <view class="notif-left">
            <view class="notif-bar" :class="getCategoryClass(item.category)"></view>
            <view class="notif-icon">{{ getCategoryIcon(item.category) }}</view>
          </view>
          <view class="notif-body">
            <view class="notif-head">
              <text class="notif-title">{{ item.title }}</text>
              <view class="notif-dot" v-if="!item.is_read"></view>
            </view>
            <text class="notif-text">{{ item.body }}</text>
            <view class="notif-foot">
              <view class="notif-category" :class="getCategoryClass(item.category)">
                <text>{{ item.category_name }}</text>
              </view>
              <text class="notif-time">{{ formatTime(item.created_at) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Empty State -->
      <view class="empty-card" v-if="notifications.length === 0">
        <text class="empty-icon">🔔</text>
        <text class="empty-title">暂无消息</text>
        <text class="empty-desc">当有新的通知时会显示在这里</text>
      </view>

      <!-- Load More -->
      <view class="load-more" v-if="notifications.length > 0 && hasMore">
        <text class="load-more-text" @click="loadMore">加载更多</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '@/utils/request'

const notifications = ref<any[]>([])
const unreadCount = ref(0)
const currentFilter = ref('')
const page = ref(1)
const hasMore = ref(true)

const categoryFilters = [
  { value: 'hazard_new', label: '新隐患' },
  { value: 'rectify_submitted', label: '已提交' },
  { value: 'ai_abnormal', label: 'AI异常' },
  { value: 'deadline_overdue', label: '逾期' },
]

const categoryClassMap: Record<string, string> = {
  hazard_new: 'cat--red',
  hazard_assigned: 'cat--blue',
  rectify_submitted: 'cat--blue',
  rectify_approved: 'cat--green',
  rectify_rejected: 'cat--red',
  inspection_overdue: 'cat--orange',
  ai_abnormal: 'cat--purple',
  deadline_approaching: 'cat--orange',
  deadline_overdue: 'cat--red',
}

const categoryIconMap: Record<string, string> = {
  hazard_new: '⚠',
  hazard_assigned: '📋',
  rectify_submitted: '📤',
  rectify_approved: '✅',
  rectify_rejected: '❌',
  inspection_overdue: '⏰',
  ai_abnormal: '🤖',
  deadline_approaching: '⏳',
  deadline_overdue: '🚨',
}

const pageReady = ref(false)

onMounted(async () => {
  await Promise.all([loadNotifications(), loadUnreadCount()])
  nextTick(() => { pageReady.value = true })
})

onShow(async () => {
  pageReady.value = false
  await Promise.all([loadNotifications(), loadUnreadCount()])
  nextTick(() => { pageReady.value = true })
})

async function loadNotifications() {
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (currentFilter.value === 'unread') {
      params.is_read = 'false'
    } else if (currentFilter.value) {
      params.category = currentFilter.value
    }
    const res: any = await api.getNotifications(params)
    notifications.value = res.results || res
    hasMore.value = notifications.value.length >= 20
  } catch (error) {
    console.error('加载通知失败:', error)
  }
}

async function loadUnreadCount() {
  try {
    const res: any = await api.getUnreadCount()
    unreadCount.value = res.total_unread || 0
  } catch (error) {
    console.error('加载未读数失败:', error)
  }
}

async function loadMore() {
  page.value++
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (currentFilter.value === 'unread') {
      params.is_read = 'false'
    } else if (currentFilter.value) {
      params.category = currentFilter.value
    }
    const res: any = await api.getNotifications(params)
    const newData = res.results || res
    notifications.value = [...notifications.value, ...newData]
    hasMore.value = newData.length >= 20
  } catch (error) {
    // 加载失败回退页码，保证下次"加载更多"拿的还是同一页
    page.value--
  }
}

function filterBy(value: string) {
  currentFilter.value = value
  page.value = 1
  loadNotifications()
}

async function handleClick(item: any) {
  if (!item.is_read) {
    try {
      await api.markRead(item.id)
      // 乐观更新本地状态，不等后端确认
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  // Navigate based on source type
  const routeMap: Record<string, string> = {
    hazard: '/pages/task/index',
    task: '/pages/task/index',
    record: '/pages/history/index',
    point: '/pages/inspect/index',
  }
  const url = routeMap[item.source_type] || '/pages/index/index'
  uni.navigateTo({ url })
}

async function markAllRead() {
  try {
    await api.markAllRead()
    notifications.value.forEach(n => { n.is_read = true })
    unreadCount.value = 0
    uni.showToast({ title: '已全部标记为已读', icon: 'success' })
  } catch (error) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function getCategoryClass(category: string): string {
  return categoryClassMap[category] || 'cat--blue'
}

function getCategoryIcon(category: string): string {
  return categoryIconMap[category] || '📌'
}

function formatTime(dateStr: string): string {
  if (!dateStr) return ''
  const now = Date.now()
  const date = new Date(dateStr).getTime()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 172800000) return '昨天'

  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f8fafc;
}

/* Header */
.page-header {
  background: linear-gradient(165deg, #0f172a 0%, #1e293b 100%);
  padding: 40rpx 32rpx 36rpx;
  position: relative;
}

.page-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 6rpx;
}

.page-subtitle {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.5);
}

.header-actions {
  position: absolute;
  right: 32rpx;
  top: 50%;
  transform: translateY(-50%);
}

.mark-all-btn {
  padding: 10rpx 20rpx;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 20rpx;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
}

/* Filters */
.filter-scroll {
  display: flex;
  gap: 16rpx;
  padding: 20rpx 32rpx;
  background: #ffffff;
  border-bottom: 1rpx solid #f1f5f9;
  overflow-x: auto;
  white-space: nowrap;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 22rpx;
  border-radius: 20rpx;
  font-size: 26rpx;
  color: #64748b;
  background: #f8fafc;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.filter-tag.active {
  background: #0f172a;
  color: #ffffff;
}

.filter-count {
  font-size: 24rpx;
  background: rgba(255, 255, 255, 0.2);
  padding: 2rpx 10rpx;
  border-radius: 10rpx;
}

/* List */
.list-section {
  padding: 20rpx 32rpx;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

/* Card */
.notif-card {
  display: flex;
  gap: 18rpx;
  background: #ffffff;
  border-radius: 18rpx;
  padding: 24rpx;
  box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.03);
  transition: all 0.15s ease;
}

.notif-card:active {
  background: #f8fafc;
}

.notif--unread {
  background: #fafbff;
  border: 1rpx solid #e8edf5;
}

.notif-left {
  display: flex;
  gap: 0;
}

.notif-bar {
  width: 5rpx;
  border-radius: 3rpx;
  flex-shrink: 0;
}

.cat--red { background: #ef4444; }
.cat--blue { background: #3b82f6; }
.cat--green { background: #10b981; }
.cat--orange { background: #f59e0b; }
.cat--purple { background: #8b5cf6; }

.notif-icon {
  font-size: 36rpx;
  flex-shrink: 0;
  width: 60rpx;
  text-align: center;
}

.notif-body {
  flex: 1;
  min-width: 0;
}

.notif-head {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 8rpx;
}

.notif-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #0f172a;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notif-dot {
  width: 12rpx;
  height: 12rpx;
  background: #ef4444;
  border-radius: 50%;
  flex-shrink: 0;
}

.notif-text {
  font-size: 28rpx;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 14rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notif-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notif-category {
  padding: 4rpx 14rpx;
  border-radius: 6rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.cat--red .notif-category { background: #fef2f2; color: #dc2626; }
.cat--blue .notif-category { background: #eff6ff; color: #2563eb; }
.cat--green .notif-category { background: #f0fdf4; color: #059669; }
.cat--orange .notif-category { background: #fffbeb; color: #d97706; }
.cat--purple .notif-category { background: #f5f3ff; color: #7c3aed; }

.notif-category text {
  font-size: 24rpx;
}

.notif-time {
  font-size: 26rpx;
  color: #64748b;
}

/* Empty */
.empty-card {
  text-align: center;
  padding: 80rpx 40rpx;
}

.empty-icon {
  display: block;
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.empty-title {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #0f172a;
  margin-bottom: 8rpx;
}

.empty-desc {
  display: block;
  font-size: 26rpx;
  color: #64748b;
}

/* Load More */
.load-more {
  text-align: center;
  padding: 32rpx;
}

.load-more-text {
  font-size: 26rpx;
  color: #06b6d4;
}
</style>
