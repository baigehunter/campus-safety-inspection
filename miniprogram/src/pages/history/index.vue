<template>
  <view class="page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">历史记录</text>
      <text class="page-subtitle">查看巡检和上报记录</text>
    </view>

    <!-- Tabs -->
    <view class="tabs-container">
      <view class="tabs">
        <view
          class="tab"
          :class="{ active: currentTab === 'record' }"
          @click="switchTab('record')"
        >
          <view class="tab-icon">
            <text>📋</text>
          </view>
          <text class="tab-label">巡检记录</text>
        </view>
        <view
          class="tab"
          :class="{ active: currentTab === 'hazard' }"
          @click="switchTab('hazard')"
        >
          <view class="tab-icon">
            <text>⚠️</text>
          </view>
          <text class="tab-label">隐患上报</text>
        </view>
      </view>
    </view>

    <!-- List -->
    <view class="list-section">
      <view class="list">
        <!-- Record Items -->
        <view class="item-card anim-fade-right" v-for="(item, index) in dataList" :key="item.id"
          :class="'delay-' + Math.min(index + 1, 8)">
          <view class="item-header">
            <view class="item-title-wrap">
              <text class="item-title">{{ item.point_name || item.title }}</text>
            </view>
            <view class="item-status" :class="`status--${item.status}`">
              <text>{{ item.status_name }}</text>
            </view>
          </view>

          <text class="item-desc" v-if="item.remark || item.description">
            {{ item.remark || item.description }}
          </text>

          <!-- AI Analysis -->
          <view class="ai-section" v-if="item.ai_analysis || item.ai_tags?.length">
            <view class="ai-head">
              <text class="ai-head-icon">🤖</text>
              <text class="ai-head-text">AI 分析</text>
              <text class="ai-status-tag" v-if="item.ai_status" :class="item.ai_status === 'abnormal' ? 'ai-status--danger' : 'ai-status--success'">
                {{ item.ai_status === 'abnormal' ? '异常' : '正常' }}
              </text>
            </view>
            <view class="ai-tags-row" v-if="item.ai_tags?.length">
              <text class="ai-tag-item" v-for="tag in item.ai_tags" :key="tag">{{ tag }}</text>
            </view>
            <text class="ai-analysis-text" v-if="item.ai_analysis">{{ item.ai_analysis }}</text>
          </view>

          <!-- Photos -->
          <view class="photo-row" v-if="getPhotos(item).length > 0">
            <image
              v-for="(photo, idx) in getPhotos(item).slice(0, 4)"
              :key="idx"
              :src="photo"
              mode="aspectFill"
              class="photo-thumb"
              @click="previewImage(getPhotos(item), idx)"
            />
            <view class="photo-more" v-if="getPhotos(item).length > 4">
              <text>+{{ getPhotos(item).length - 4 }}</text>
            </view>
          </view>

          <view class="item-footer">
            <view class="footer-left">
              <text class="footer-icon">📅</text>
              <text class="footer-text">{{ formatDateTime(item.inspection_time || item.created_at) }}</text>
            </view>
            <view class="footer-right" v-if="item.hazard_type_name">
              <view class="type-tag">
                <text>{{ item.hazard_type_name }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="empty-state" v-if="dataList.length === 0">
        <view class="empty-icon">
          <text>📭</text>
        </view>
        <text class="empty-title">暂无记录</text>
        <text class="empty-desc">{{ currentTab === 'record' ? '开始巡检后记录会显示在这里' : '上报隐患后记录会显示在这里' }}</text>
      </view>

      <!-- Load More -->
      <view class="load-more" v-if="dataList.length > 0 && hasMore">
        <text class="load-more-text" @click="loadMore">加载更多</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '@/utils/request'

const currentTab = ref('record')
const dataList = ref<any[]>([])
const page = ref(1)
const hasMore = ref(true)

const pageReady = ref(false)

onMounted(loadData)

onShow(() => {
  pageReady.value = false
  nextTick(() => { pageReady.value = true })
})

async function loadData() {
  page.value = 1
  hasMore.value = true
  try {
    const res: any = await fetchData(1)
    dataList.value = res.results || res || []
    hasMore.value = dataList.value.length >= 20
  } catch (error) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

async function loadMore() {
  page.value++
  try {
    const res: any = await fetchData(page.value)
    const newData = res.results || res || []
    dataList.value = [...dataList.value, ...newData]
    hasMore.value = newData.length >= 20
  } catch (error) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

// 两个 tab 共用列表 UI，数据源不同但接口格式一致，简单 switch 一下
async function fetchData(p: number) {
  if (currentTab.value === 'record') {
    return await api.getRecords({ page: p, page_size: 20 })
  } else {
    return await api.getHazards({ page: p, page_size: 20 })
  }
}

function switchTab(tab: string) {
  currentTab.value = tab
  loadData()
}

function getPhotos(item: any) {
  return item.inspection_photos || item.photos || []
}

function previewImage(photos: string[], current: number) {
  uni.previewImage({
    urls: photos,
    current
  })
}

function formatDateTime(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hour}:${minute}`
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f8fafc;
}

/* Page Header */
.page-header {
  background: linear-gradient(165deg, #0f172a 0%, #1e293b 100%);
  padding: 32rpx 32rpx 48rpx;
}

.page-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8rpx;
}

.page-subtitle {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.5);
}

/* Tabs */
.tabs-container {
  padding: 0 32rpx;
  margin-top: -24rpx;
  position: relative;
  z-index: 10;
}

.tabs {
  display: flex;
  gap: 16rpx;
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx;
  background: #ffffff;
  border-radius: 20rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.tab.active {
  background: #0f172a;
}

.tab-icon {
  font-size: 32rpx;
}

.tab-label {
  font-size: 28rpx;
  font-weight: 500;
  color: #0f172a;
}

.tab.active .tab-label {
  color: #ffffff;
}

/* List Section */
.list-section {
  padding: 24rpx 32rpx;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

/* Item Card */
.item-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.item-title-wrap {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #0f172a;
}

.item-status {
  padding: 6rpx 14rpx;
  border-radius: 10rpx;
  flex-shrink: 0;
}

.item-status text {
  font-size: 26rpx;
  font-weight: 500;
}

.status--normal { background: #d1fae5; }
.status--normal text { color: #059669; }
.status--abnormal { background: #fee2e2; }
.status--abnormal text { color: #dc2626; }
.status--pending { background: #fef3c7; }
.status--pending text { color: #b45309; }
.status--assigned { background: #dbeafe; }
.status--assigned text { color: #1d4ed8; }
.status--rectifying { background: #ffedd5; }
.status--rectifying text { color: #c2410c; }
.status--completed { background: #d1fae5; }
.status--completed text { color: #059669; }
.status--rejected { background: #fee2e2; }
.status--rejected text { color: #dc2626; }

.item-desc {
  font-size: 26rpx;
  color: #64748b;
  margin-bottom: 16rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* AI Section */
.ai-section {
  background: #fafafe;
  border: 1rpx solid #e8e8f0;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
}

.ai-head {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 10rpx;
}

.ai-head-icon {
  font-size: 28rpx;
}

.ai-head-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #4f46e5;
}

.ai-status-tag {
  font-size: 24rpx;
  padding: 2rpx 10rpx;
  border-radius: 6rpx;
  margin-left: auto;
}

.ai-status--success {
  background: #d1fae5;
  color: #059669;
}

.ai-status--danger {
  background: #fee2e2;
  color: #dc2626;
}

.ai-tags-row {
  display: flex;
  gap: 8rpx;
  flex-wrap: wrap;
  margin-bottom: 10rpx;
}

.ai-tag-item {
  font-size: 24rpx;
  color: #4f46e5;
  background: #eef2ff;
  padding: 4rpx 12rpx;
  border-radius: 16rpx;
}

.ai-analysis-text {
  font-size: 28rpx;
  color: #475569;
  line-height: 1.6;
}

/* Photos */
.photo-row {
  display: flex;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.photo-thumb {
  width: 140rpx;
  height: 140rpx;
  border-radius: 12rpx;
  object-fit: cover;
}

.photo-more {
  width: 140rpx;
  height: 140rpx;
  border-radius: 12rpx;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.photo-more text {
  font-size: 28rpx;
  font-weight: 600;
  color: #ffffff;
}

/* Footer */
.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.footer-icon {
  font-size: 26rpx;
}

.footer-text {
  font-size: 28rpx;
  color: #64748b;
}

.type-tag {
  padding: 4rpx 12rpx;
  background: #f1f5f9;
  border-radius: 8rpx;
}

.type-tag text {
  font-size: 26rpx;
  color: #64748b;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
}

.empty-icon {
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
