<template>
  <view class="page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">巡检点位</text>
      <text class="page-subtitle">选择点位开始巡检</text>
    </view>

    <!-- Search Bar -->
    <view class="search-bar">
      <view class="search-input-wrap">
        <text class="search-icon">🔍</text>
        <input
          v-model="searchText"
          placeholder="搜索点位名称或位置"
          class="search-input"
          placeholder-class="search-placeholder"
          @input="filterPoints"
        />
      </view>
    </view>

    <!-- Points List -->
    <view class="points-section">
      <view class="points-list">
        <view
          class="point-card anim-fade-right btn-press"
          v-for="(point, index) in filteredPoints"
          :key="point.id"
          :class="'delay-' + Math.min(index + 1, 8)"
          @click="selectPoint(point)"
        >
          <view class="point-indicator">
            <view class="indicator-dot"></view>
          </view>
          <view class="point-content">
            <view class="point-header">
              <text class="point-name">{{ point.name }}</text>
              <text class="point-code">{{ point.code }}</text>
            </view>
            <view class="point-location">
              <text class="location-icon">📍</text>
              <text class="location-text">{{ point.area_name }} · {{ point.location }}</text>
            </view>
            <view class="point-meta">
              <view class="meta-tag">
                <text>{{ getFrequencyLabel(point.inspection_frequency) }}</text>
              </view>
            </view>
          </view>
          <view class="point-arrow">
            <text>›</text>
          </view>
        </view>
      </view>

      <view class="empty-state" v-if="filteredPoints.length === 0 && points.length > 0">
        <text class="empty-icon">🔍</text>
        <text class="empty-text">未找到匹配的点位</text>
      </view>

      <view class="empty-state" v-if="points.length === 0">
        <text class="empty-icon">📋</text>
        <text class="empty-text">暂无巡检点位</text>
        <text class="empty-desc">请联系管理员添加巡检点位</text>
      </view>
    </view>

    <!-- Inspection Form Popup -->
    <view class="popup" v-if="showForm">
      <view class="popup-mask mask-fade" @click="showForm = false"></view>
      <view class="popup-content anim-slide-up">
        <view class="popup-header">
          <view class="popup-title-wrap">
            <text class="popup-title">巡检记录</text>
            <text class="popup-subtitle">{{ selectedPoint?.name }}</text>
          </view>
          <view class="popup-close" @click="showForm = false">
            <text>✕</text>
          </view>
        </view>

        <view class="form">
          <!-- Status Selection -->
          <view class="form-section">
            <text class="form-label">巡检状态</text>
            <view class="status-options">
              <view
                class="status-option"
                :class="{ active: form.status === 'normal' }"
                @click="form.status = 'normal'"
              >
                <view class="status-icon status-icon--success">
                  <text>✓</text>
                </view>
                <text class="status-text">正常</text>
              </view>
              <view
                class="status-option"
                :class="{ active: form.status === 'abnormal' }"
                @click="form.status = 'abnormal'"
              >
                <view class="status-icon status-icon--danger">
                  <text>!</text>
                </view>
                <text class="status-text">异常</text>
              </view>
            </view>
          </view>

          <!-- Photos -->
          <view class="form-section">
            <text class="form-label">现场照片</text>
            <text class="form-hint">请上传清晰的现场照片（至少1张）</text>
            <view class="photo-grid">
              <view class="photo-item" v-for="(photo, idx) in form.photos" :key="idx">
                <image :src="photo" mode="aspectFill" class="photo-image" />
                <view class="photo-remove" @click="removePhoto(idx)">
                  <text>✕</text>
                </view>
              </view>
              <view class="photo-add" @click="showImagePicker" v-if="form.photos.length < 3">
                <view class="add-icon">
                  <text>➕</text>
                </view>
                <text class="add-text">上传图片</text>
              </view>
            </view>
          </view>

          <!-- Remark -->
          <view class="form-section">
            <text class="form-label">备注说明</text>
            <textarea
              v-model="form.remark"
              placeholder="请输入巡检备注（选填）"
              class="form-textarea"
              placeholder-class="textarea-placeholder"
            />
          </view>

          <!-- AI Smart Analysis -->
          <view class="form-section">
            <text class="form-label">AI 智能分析</text>
            <text class="form-hint">根据照片和备注自动判断巡检状态</text>
            <button
              class="btn-analyze"
              @click="analyzeInspection"
              :disabled="analyzing || form.photos.length === 0"
            >
              <text v-if="!analyzing">智能分析</text>
              <text v-else>分析中...</text>
            </button>
          </view>

          <!-- AI Result Card -->
          <view class="ai-result-card" v-if="aiResult">
            <view class="ai-result-head">
              <text class="ai-result-title">AI 分析结果</text>
              <text class="ai-result-badge">自动填充</text>
            </view>
            <view class="ai-result-row">
              <text class="ai-result-label">判断状态</text>
              <text :class="['ai-result-value', aiResult.status === 'abnormal' ? 'text-danger' : 'text-success']">
                {{ aiResult.status === 'abnormal' ? '异常' : '正常' }}
              </text>
            </view>
            <view class="ai-result-row" v-if="aiResult.tags && aiResult.tags.length">
              <text class="ai-result-label">AI 标签</text>
              <view class="ai-tags">
                <text class="ai-tag" v-for="tag in aiResult.tags" :key="tag">{{ tag }}</text>
              </view>
            </view>
            <view class="ai-result-analysis" v-if="aiResult.analysis">
              <text class="ai-result-label">分析结论</text>
              <text class="ai-analysis-text">{{ aiResult.analysis }}</text>
            </view>
          </view>

          <!-- Submit Button -->
          <button class="btn-submit" @click="submitInspection" :disabled="submitting">
            <text v-if="!submitting">提交巡检</text>
            <text v-else>提交中...</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api, uploadImages } from '@/utils/request'
import { requestSubscribe } from '@/utils/subscribe'

const points = ref<any[]>([])
const searchText = ref('')
const showForm = ref(false)
const selectedPoint = ref<any>(null)
const submitting = ref(false)
const analyzing = ref(false)
const aiResult = ref<any>(null)

const form = ref({
  status: 'normal',
  photos: [] as string[],
  remark: ''
})

const filteredPoints = computed(() => {
  if (!searchText.value) return points.value
  const keyword = searchText.value.toLowerCase()
  return points.value.filter(p =>
    p.name?.toLowerCase().includes(keyword) ||
    p.location?.toLowerCase().includes(keyword) ||
    p.area_name?.toLowerCase().includes(keyword)
  )
})

const pageReady = ref(false)

onMounted(loadPoints)

onShow(() => {
  // 每次切到这一页都重新触发入场动画。pageReady 先关再开，
  // 利用 nextTick 让 Vue 重新挂载动画 class
  pageReady.value = false
  nextTick(() => { pageReady.value = true })
})

async function loadPoints() {
  try {
    const res: any = await api.getPoints({ is_active: 'true' })
    points.value = res.results || res || []
  } catch (error) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function selectPoint(point: any) {
  selectedPoint.value = point
  form.value = { status: 'normal', photos: [], remark: '' }
  aiResult.value = null
  showForm.value = true
}

function showImagePicker() {
  uni.showActionSheet({
    itemList: ['拍照', '从相册选择'],
    success: (res) => {
      if (res.tapIndex === 0) {
        chooseImage(['camera'])
      } else if (res.tapIndex === 1) {
        chooseImage(['album'])
      }
    }
  })
}

function chooseImage(sourceType: string[]) {
  const remaining = 3 - form.value.photos.length
  uni.chooseImage({
    count: remaining,
    sizeType: ['compressed'],
    sourceType: sourceType,
    success: (res) => {
      form.value.photos.push(...res.tempFilePaths)
    }
  })
}

function takePhoto() {
  chooseImage(['camera'])
}

function removePhoto(idx: number) {
  form.value.photos.splice(idx, 1)
}

function photoToBase64(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    // #ifdef MP-WEIXIN
    const fs = uni.getFileSystemManager()
    fs.readFile({
      filePath: filePath,
      encoding: 'base64',
      success: (res: any) => resolve(res.data as string),
      fail: (err: any) => reject(err)
    })
    // #endif
    // #ifdef H5
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')!
      ctx.drawImage(img, 0, 0)
      const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
      resolve(dataUrl.split(',')[1])
    }
    img.onerror = reject
    img.src = filePath
    // #endif
  })
}

async function analyzeInspection() {
  if (form.value.photos.length === 0) {
    uni.showToast({ title: '请先上传照片', icon: 'none' })
    return
  }

  analyzing.value = true
  uni.showLoading({ title: 'AI分析中...' })

  try {
    const base64Photos: string[] = []
    for (const path of form.value.photos) {
      const b64 = await photoToBase64(path)
      base64Photos.push(b64)
    }

    const result: any = await api.analyzeInspection({
      description: form.value.remark,
      photos: base64Photos
    })

    aiResult.value = result

    // AI 自动判断巡检状态，但用户可以手动改
    if (result.status) {
      form.value.status = result.status
    }

    uni.hideLoading()
    uni.showToast({ title: 'AI分析完成', icon: 'success' })
  } catch (error: any) {
    uni.hideLoading()
    const msg = error?.message || 'AI分析失败，请手动判断'
    uni.showToast({ title: msg, icon: 'none' })
  } finally {
    analyzing.value = false
  }
}

async function submitInspection() {
  if (!selectedPoint.value) return
  if (form.value.photos.length === 0) {
    uni.showToast({ title: '请上传现场照片', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    uni.showLoading({ title: '上传中...' })
    const uploadedUrls = await uploadImages(form.value.photos)
    uni.hideLoading()

    if (uploadedUrls.length === 0) {
      uni.showToast({ title: '图片上传失败', icon: 'none' })
      submitting.value = false
      return
    }

    await api.createRecord({
      point: selectedPoint.value.id,
      status: form.value.status,
      inspection_photos: uploadedUrls,
      remark: form.value.remark,
      ai_status: aiResult.value?.status || '',
      ai_tags: aiResult.value?.tags || [],
      ai_analysis: aiResult.value?.analysis || ''
    })
    // 微信限制：订阅弹窗必须从点击事件的同步回调链里调起。
    // 所以先 requestSubscribe 再关弹窗，反过来就不行。
    requestSubscribe(['ai_abnormal'])
    uni.showToast({ title: '提交成功', icon: 'success' })
    showForm.value = false
  } catch (error: any) {
    uni.hideLoading()
    uni.showToast({ title: error.message || '提交失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

function getFrequencyLabel(frequency: string) {
  const map: Record<string, string> = {
    daily: '每日巡检',
    weekly: '每周巡检',
    monthly: '每月巡检'
  }
  return map[frequency] || frequency
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

/* Search */
.search-bar {
  padding: 0 32rpx;
  margin-top: -24rpx;
  position: relative;
  z-index: 10;
}

.search-input-wrap {
  display: flex;
  align-items: center;
  background: #ffffff;
  border-radius: 20rpx;
  padding: 0 24rpx;
  height: 88rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08);
}

.search-icon {
  font-size: 28rpx;
  margin-right: 16rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #0f172a;
}

.search-placeholder {
  color: #64748b;
}

/* Points Section */
.points-section {
  padding: 24rpx 32rpx;
}

.points-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.point-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.point-indicator {
  width: 8rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
}

.indicator-dot {
  width: 8rpx;
  height: 8rpx;
  background: #06b6d4;
  border-radius: 50%;
  box-shadow: 0 0 12rpx #06b6d4;
}

.point-content {
  flex: 1;
  min-width: 0;
}

.point-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.point-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #0f172a;
}

.point-code {
  font-size: 24rpx;
  color: #64748b;
  background: #f1f5f9;
  padding: 4rpx 10rpx;
  border-radius: 6rpx;
}

.point-location {
  display: flex;
  align-items: center;
  gap: 6rpx;
  margin-bottom: 8rpx;
}

.location-icon {
  font-size: 26rpx;
}

.location-text {
  font-size: 28rpx;
  color: #64748b;
}

.point-meta {
  display: flex;
  gap: 12rpx;
}

.meta-tag {
  font-size: 24rpx;
  color: #0891b2;
  background: #ecfeff;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.point-arrow {
  font-size: 36rpx;
  color: #cbd5e1;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
}

.empty-icon {
  display: block;
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.empty-text {
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

/* Popup */
.popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.popup-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
}

.popup-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ffffff;
  border-radius: 40rpx 40rpx 0 0;
  max-height: 85vh;
  overflow-y: auto;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32rpx;
  border-bottom: 1rpx solid #f1f5f9;
}

.popup-title-wrap {
  display: flex;
  flex-direction: column;
}

.popup-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #0f172a;
}

.popup-subtitle {
  font-size: 26rpx;
  color: #64748b;
  margin-top: 4rpx;
}

.popup-close {
  width: 56rpx;
  height: 56rpx;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 28rpx;
}

/* Form */
.form {
  padding: 24rpx 32rpx 48rpx;
}

.form-section {
  margin-bottom: 32rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 8rpx;
}

.form-hint {
  display: block;
  font-size: 28rpx;
  color: #64748b;
  margin-bottom: 16rpx;
}

/* Status Options */
.status-options {
  display: flex;
  gap: 20rpx;
}

.status-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32rpx 24rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 20rpx;
  transition: all 0.2s ease;
}

.status-option.active {
  background: #f0fdfa;
  border-color: #06b6d4;
}

.status-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.status-icon--success {
  background: #d1fae5;
  color: #059669;
}

.status-icon--danger {
  background: #fee2e2;
  color: #dc2626;
}

.status-text {
  font-size: 28rpx;
  font-weight: 500;
  color: #0f172a;
}

/* Photo Grid */
.photo-grid {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.photo-item {
  position: relative;
  width: 180rpx;
  height: 180rpx;
}

.photo-image {
  width: 100%;
  height: 100%;
  border-radius: 16rpx;
  object-fit: cover;
}

.photo-remove {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  width: 44rpx;
  height: 44rpx;
  background: #f43f5e;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  box-shadow: 0 4rpx 12rpx rgba(244, 63, 94, 0.3);
}

.photo-add {
  width: 180rpx;
  height: 180rpx;
  border: 2rpx dashed #cbd5e1;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.add-icon {
  font-size: 44rpx;
  margin-bottom: 8rpx;
}

.add-text {
  font-size: 28rpx;
  color: #64748b;
}

/* Textarea */
.form-textarea {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #0f172a;
}

.textarea-placeholder {
  color: #64748b;
}

/* AI Analyze */
.btn-analyze {
  width: 100%;
  height: 84rpx;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #ffffff;
  border: none;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  box-shadow: 0 8rpx 24rpx rgba(99, 102, 241, 0.22);
}

.btn-analyze:disabled {
  opacity: 0.5;
}

/* AI Result Card */
.ai-result-card {
  background: #fafafe;
  border: 2rpx solid #6366f1;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 32rpx;
}

.ai-result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.ai-result-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #4f46e5;
}

.ai-result-badge {
  font-size: 24rpx;
  color: #6366f1;
  background: #eef2ff;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.ai-result-row {
  display: flex;
  align-items: center;
  padding: 10rpx 0;
}

.ai-result-label {
  font-size: 26rpx;
  color: #64748b;
  width: 130rpx;
  flex-shrink: 0;
}

.ai-result-value {
  font-size: 26rpx;
  font-weight: 600;
  color: #0f172a;
}

.text-danger { color: #dc2626; }
.text-success { color: #059669; }

.ai-tags {
  display: flex;
  gap: 8rpx;
  flex-wrap: wrap;
}

.ai-tag {
  font-size: 26rpx;
  color: #4f46e5;
  background: #eef2ff;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

.ai-result-analysis {
  padding-top: 14rpx;
}

.ai-analysis-text {
  display: block;
  font-size: 28rpx;
  color: #475569;
  margin-top: 8rpx;
  line-height: 1.6;
}

/* Submit Button */
.btn-submit {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: #ffffff;
  border: none;
  border-radius: 20rpx;
  font-size: 32rpx;
  font-weight: 600;
  margin-top: 24rpx;
  box-shadow: 0 12rpx 32rpx rgba(6, 182, 212, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
}
</style>
