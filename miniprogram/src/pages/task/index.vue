<template>
  <view class="page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">整改任务</text>
      <text class="page-subtitle">处理分配的整改任务</text>
    </view>

    <!-- Tabs -->
    <view class="tabs-container">
      <view class="tabs">
        <view
          class="tab"
          :class="{ active: currentTab === 'pending' }"
          @click="switchTab('pending')"
        >
          <text class="tab-label">待处理</text>
          <view class="tab-badge" v-if="counts.pending > 0">
            <text>{{ counts.pending }}</text>
          </view>
        </view>
        <view
          class="tab"
          :class="{ active: currentTab === 'submitted' }"
          @click="switchTab('submitted')"
        >
          <text class="tab-label">待验收</text>
          <view class="tab-badge tab-badge--blue" v-if="counts.submitted > 0">
            <text>{{ counts.submitted }}</text>
          </view>
        </view>
        <view
          class="tab"
          :class="{ active: currentTab === 'completed' }"
          @click="switchTab('completed')"
        >
          <text class="tab-label">已完成</text>
        </view>
      </view>
    </view>

    <!-- Task List -->
    <view class="task-section">
      <view class="task-list">
        <view
          class="task-card anim-fade-right btn-press"
          v-for="(task, index) in tasks"
          :key="task.id"
          :class="'delay-' + Math.min(index + 1, 8)"
          @click="handleTaskClick(task)"
        >
          <view class="task-priority" :class="getPriorityClass(task.deadline)"></view>
          <view class="task-content">
            <view class="task-header">
              <text class="task-title">{{ task.hazard_title }}</text>
              <view class="task-status" :class="`status--${task.status}`">
                <text>{{ task.status_name }}</text>
              </view>
            </view>

            <text class="task-desc">{{ task.description || '暂无整改要求' }}</text>

            <view class="task-meta">
              <view class="meta-item">
                <text class="meta-icon">📅</text>
                <text class="meta-text">截止 {{ formatDate(task.deadline) }}</text>
              </view>
              <view class="meta-item" v-if="task.assigner_name">
                <text class="meta-icon">👤</text>
                <text class="meta-text">{{ task.assigner_name }} 派单</text>
              </view>
            </view>

            <view class="task-action" v-if="canSubmit(task)">
              <text class="action-text">点击提交整改</text>
              <text class="action-arrow">›</text>
            </view>
          </view>
        </view>
      </view>

      <view class="empty-state" v-if="tasks.length === 0">
        <view class="empty-icon">
          <text>{{ currentTab === 'completed' ? '🎉' : '📋' }}</text>
        </view>
        <text class="empty-title">{{ getEmptyText() }}</text>
        <text class="empty-desc">{{ getEmptyDesc() }}</text>
      </view>
    </view>

    <!-- Submit Popup -->
    <view class="popup" v-if="showPopup">
      <view class="popup-mask mask-fade" @click="showPopup = false"></view>
      <view class="popup-content anim-slide-up">
        <view class="popup-header">
          <view class="popup-title-wrap">
            <text class="popup-title">提交整改</text>
            <text class="popup-subtitle">{{ selectedTask?.hazard_title }}</text>
          </view>
          <view class="popup-close" @click="showPopup = false">
            <text>✕</text>
          </view>
        </view>

        <view class="form">
          <view class="form-section">
            <text class="form-label">整改后照片</text>
            <text class="form-hint">请上传整改完成后的现场照片</text>
            <view class="photo-grid">
              <view class="photo-item" v-for="(photo, idx) in rectifyForm.photos" :key="idx">
                <image :src="photo" mode="aspectFill" class="photo-image" />
                <view class="photo-remove" @click="removePhoto(idx)">
                  <text>✕</text>
                </view>
              </view>
              <view class="photo-add" @click="showImagePicker" v-if="rectifyForm.photos.length < 5">
                <view class="add-icon">
                  <text>➕</text>
                </view>
                <text class="add-text">上传图片</text>
              </view>
            </view>
          </view>

          <view class="form-section">
            <text class="form-label">整改说明</text>
            <textarea
              v-model="rectifyForm.remark"
              placeholder="请描述整改完成情况（选填）"
              class="form-textarea"
              placeholder-class="textarea-placeholder"
            />
          </view>

          <button class="btn-submit" @click="submitRectify" :disabled="submitting">
            <text v-if="!submitting">确认提交</text>
            <text v-else>提交中...</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api, uploadImages } from '@/utils/request'
import { requestSubscribe } from '@/utils/subscribe'

const currentTab = ref('pending')
const tasks = ref<any[]>([])
const showPopup = ref(false)
const selectedTask = ref<any>(null)
const submitting = ref(false)

const counts = reactive({
  pending: 0,
  submitted: 0
})

const rectifyForm = ref({
  photos: [] as string[],
  remark: ''
})

const pageReady = ref(false)

onMounted(loadTasks)

onShow(() => {
  pageReady.value = false
  nextTick(() => { pageReady.value = true })
})

async function loadTasks() {
  try {
    const res: any = await api.getTasks({ status: currentTab.value, page_size: 50 })
    tasks.value = res.results || res || []

    // 分别拉三个 tab 的计数——后端没有单独的 count 接口，
    // 所以用 page_size=1 取第一条顺便拿 total count，有点浪费但能用
    const pendingRes: any = await api.getTasks({ status: 'pending', page_size: 1 })
    const submittedRes: any = await api.getTasks({ status: 'submitted', page_size: 1 })
    counts.pending = pendingRes.count || 0
    counts.submitted = submittedRes.count || 0
  } catch (error) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function switchTab(tab: string) {
  currentTab.value = tab
  loadTasks()
}

function handleTaskClick(task: any) {
  if (canSubmit(task)) {
    selectedTask.value = task
    rectifyForm.value = { photos: [], remark: '' }
    showPopup.value = true
  }
}

function canSubmit(task: any) {
  return task.status === 'pending' || task.status === 'rejected'
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
  const remaining = 5 - rectifyForm.value.photos.length
  uni.chooseImage({
    count: remaining,
    sizeType: ['compressed'],
    sourceType: sourceType,
    success: (res) => {
      rectifyForm.value.photos.push(...res.tempFilePaths)
    }
  })
}

function takePhoto() {
  chooseImage(['camera'])
}

function removePhoto(idx: number) {
  rectifyForm.value.photos.splice(idx, 1)
}

async function submitRectify() {
  if (!selectedTask.value) return
  if (rectifyForm.value.photos.length === 0) {
    uni.showToast({ title: '请上传整改后照片', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    uni.showLoading({ title: '上传中...' })
    const uploadedUrls = await uploadImages(rectifyForm.value.photos)
    uni.hideLoading()

    if (uploadedUrls.length === 0) {
      uni.showToast({ title: '图片上传失败', icon: 'none' })
      submitting.value = false
      return
    }

    await api.submitRectify(selectedTask.value.id, {
      photos: uploadedUrls,
      remark: rectifyForm.value.remark
    })
    requestSubscribe(['rectify_result'])
    uni.showToast({ title: '提交成功', icon: 'success' })
    showPopup.value = false
    loadTasks()
  } catch (error: any) {
    uni.hideLoading()
    uni.showToast({ title: error.message || '提交失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

function getPriorityClass(deadline: string) {
  if (!deadline) return 'priority-normal'
  const diff = new Date(deadline).getTime() - Date.now()
  if (diff < 0) return 'priority-overdue'
  if (diff < 24 * 60 * 60 * 1000) return 'priority-urgent'
  if (diff < 3 * 24 * 60 * 60 * 1000) return 'priority-high'
  return 'priority-normal'
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function getEmptyText() {
  const texts: Record<string, string> = {
    pending: '暂无待处理任务',
    submitted: '暂无待验收任务',
    completed: '暂无已完成任务'
  }
  return texts[currentTab.value]
}

function getEmptyDesc() {
  const descs: Record<string, string> = {
    pending: '新任务分配后会显示在这里',
    submitted: '提交的整改等待管理员验收',
    completed: '验收通过的任务会显示在这里'
  }
  return descs[currentTab.value]
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
  background: #ffffff;
  border-radius: 20rpx;
  padding: 8rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08);
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 20rpx 16rpx;
  border-radius: 14rpx;
  transition: all 0.2s ease;
}

.tab.active {
  background: #0f172a;
}

.tab-label {
  font-size: 28rpx;
  font-weight: 500;
  color: #64748b;
}

.tab.active .tab-label {
  color: #ffffff;
}

.tab-badge {
  min-width: 36rpx;
  height: 36rpx;
  background: #f43f5e;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
}

.tab-badge text {
  font-size: 24rpx;
  font-weight: 600;
  color: #ffffff;
}

.tab-badge--blue {
  background: #3b82f6;
}

/* Task Section */
.task-section {
  padding: 24rpx 32rpx;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.task-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  gap: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.task-priority {
  width: 6rpx;
  border-radius: 3rpx;
  flex-shrink: 0;
}

.priority-overdue { background: #f43f5e; }
.priority-urgent { background: #f59e0b; }
.priority-high { background: #fb923c; }
.priority-normal { background: #10b981; }

.task-content {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.task-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #0f172a;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-status {
  padding: 6rpx 14rpx;
  border-radius: 10rpx;
  flex-shrink: 0;
}

.task-status text {
  font-size: 26rpx;
  font-weight: 500;
}

.status--pending { background: #fef3c7; }
.status--pending text { color: #b45309; }
.status--processing { background: #dbeafe; }
.status--processing text { color: #1d4ed8; }
.status--submitted { background: #e0e7ff; }
.status--submitted text { color: #4f46e5; }
.status--completed { background: #d1fae5; }
.status--completed text { color: #059669; }
.status--rejected { background: #fee2e2; }
.status--rejected text { color: #dc2626; }

.task-desc {
  font-size: 26rpx;
  color: #64748b;
  margin-bottom: 16rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-meta {
  display: flex;
  gap: 24rpx;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.meta-icon {
  font-size: 26rpx;
}

.meta-text {
  font-size: 28rpx;
  color: #64748b;
}

.task-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #f1f5f9;
}

.action-text {
  font-size: 26rpx;
  color: #06b6d4;
  font-weight: 500;
}

.action-arrow {
  font-size: 32rpx;
  color: #06b6d4;
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
