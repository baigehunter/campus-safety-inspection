<template>
  <view class="page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">上报隐患</text>
      <text class="page-subtitle">发现安全隐患请及时上报</text>
    </view>

    <!-- Form -->
    <view class="form-container">
      <!-- Title -->
      <view class="form-card anim-fade-up" :class="{ 'anim-fade-up delay-1': pageReady }">
        <view class="form-item">
          <view class="item-header">
            <text class="item-label">隐患标题</text>
            <text class="item-required">*</text>
          </view>
          <input
            v-model="form.title"
            placeholder="请简要描述隐患问题"
            class="form-input"
            placeholder-class="input-placeholder"
          />
        </view>
      </view>

      <!-- Type & Level -->
      <view class="form-card">
        <view class="form-item">
          <view class="item-header">
            <text class="item-label">隐患类型</text>
            <text class="item-required">*</text>
          </view>
          <picker :value="typeIndex" :range="typeOptions" range-key="label" @change="onTypeChange">
            <view class="form-picker">
              <text :class="{ 'picker-placeholder': typeIndex === -1 }">
                {{ typeIndex >= 0 ? typeOptions[typeIndex].label : '请选择隐患类型' }}
              </text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>

        <view class="form-divider"></view>

        <view class="form-item">
          <view class="item-header">
            <text class="item-label">隐患等级</text>
          </view>
          <view class="level-options">
            <view
              class="level-option"
              :class="{ active: form.level === 'general' }"
              @click="form.level = 'general'"
            >
              <view class="level-icon level-icon--warning">
                <text>!</text>
              </view>
              <view class="level-info">
                <text class="level-label">一般隐患</text>
                <text class="level-desc">风险较小</text>
              </view>
            </view>
            <view
              class="level-option"
              :class="{ active: form.level === 'serious' }"
              @click="form.level = 'serious'"
            >
              <view class="level-icon level-icon--danger">
                <text>⚠</text>
              </view>
              <view class="level-info">
                <text class="level-label">重大隐患</text>
                <text class="level-desc">风险较大</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- Location -->
      <view class="form-card">
        <view class="form-item">
          <view class="item-header">
            <text class="item-label">隐患位置</text>
            <text class="item-required">*</text>
          </view>
          <input
            v-model="form.location"
            placeholder="请输入具体位置（如：教学楼A栋3楼走廊）"
            class="form-input"
            placeholder-class="input-placeholder"
          />
        </view>
      </view>

      <!-- Description -->
      <view class="form-card">
        <view class="form-item">
          <view class="item-header">
            <text class="item-label">隐患描述</text>
            <text class="item-required">*</text>
          </view>
          <textarea
            v-model="form.description"
            placeholder="请详细描述隐患情况、可能造成的后果等"
            class="form-textarea"
            placeholder-class="input-placeholder"
            :maxlength="500"
          />
          <text class="char-count">{{ form.description.length }}/500</text>
        </view>
      </view>

      <!-- Photos -->
      <view class="form-card">
        <view class="form-item">
          <view class="item-header">
            <text class="item-label">现场照片</text>
            <text class="item-required">*</text>
          </view>
          <text class="item-hint">请上传清晰的现场照片，最多5张</text>
          <view class="photo-grid">
            <view class="photo-item" v-for="(photo, idx) in form.photos" :key="idx">
              <image :src="photo" mode="aspectFill" class="photo-image" />
              <view class="photo-remove" @click="removePhoto(idx)">
                <text>✕</text>
              </view>
            </view>
            <view class="photo-add" @click="showImagePicker" v-if="form.photos.length < 5">
              <view class="add-icon">
                <text>➕</text>
              </view>
              <text class="add-text">上传图片</text>
              <text class="add-count">{{ form.photos.length }}/5</text>
            </view>
          </view>
        </view>
      </view>

      <!-- AI Smart Analysis -->
      <view class="form-card">
        <view class="form-item">
          <view class="item-header">
            <text class="item-label">AI 智能分析</text>
          </view>
          <text class="item-hint">根据描述和照片自动识别隐患类型与等级</text>
          <button
            class="btn-analyze"
            @click="analyzeHazard"
            :disabled="analyzing || form.photos.length === 0"
          >
            <text v-if="!analyzing">智能分析</text>
            <text v-else>分析中...</text>
          </button>
        </view>
      </view>

      <!-- AI Result Card -->
      <view class="form-card ai-result-card" v-if="aiResult">
        <view class="ai-result-header">
          <text class="ai-result-title">AI 分析结果</text>
          <text class="ai-result-badge">自动填充</text>
        </view>
        <view class="ai-result-row">
          <text class="ai-result-label">识别类型</text>
          <text class="ai-result-value">{{ aiResult.hazard_type_name }}</text>
        </view>
        <view class="ai-result-row">
          <text class="ai-result-label">隐患等级</text>
          <text :class="['ai-result-value', aiResult.level === 'serious' ? 'text-danger' : 'text-warning']">
            {{ aiResult.level === 'serious' ? '重大隐患' : '一般隐患' }}
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

      <!-- Submit -->
      <view class="submit-section">
        <button class="btn-submit" @click="submitHazard" :disabled="submitting">
          <text v-if="!submitting">提交上报</text>
          <text v-else>提交中...</text>
        </button>
        <text class="submit-hint">上报后将由管理员进行审核派单</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api, uploadImages } from '@/utils/request'
import { requestSubscribe } from '@/utils/subscribe'

const typeOptions = [
  { value: 'fire', label: '消防安全' },
  { value: 'electric', label: '用电安全' },
  { value: 'building', label: '建筑安全' },
  { value: 'equipment', label: '设备安全' },
  { value: 'food', label: '食品安全' },
  { value: 'other', label: '其他' }
]

const typeIndex = ref(-1)
const submitting = ref(false)
const analyzing = ref(false)
const pageReady = ref(false)
const aiResult = ref<any>(null)

const typeMap: Record<string, string> = {
  fire: '消防安全',
  electric: '用电安全',
  building: '建筑安全',
  equipment: '设备安全',
  food: '食品安全',
  other: '其他'
}

// typeMap 和 typeOptions 看着重复，但用途不同：
// typeOptions 给 picker 组件用（需要 value/label 结构），
// typeMap 给 AI 结果转中文名用。合并成一个反而麻烦。


const form = ref({
  title: '',
  hazard_type: '',
  level: 'general',
  location: '',
  description: '',
  photos: [] as string[]
})

onMounted(() => {
  nextTick(() => { pageReady.value = true })
})

onShow(() => {
  pageReady.value = false
  nextTick(() => { pageReady.value = true })
})

function onTypeChange(e: any) {
  typeIndex.value = e.detail.value
  form.value.hazard_type = typeOptions[typeIndex.value].value
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
  const remaining = 5 - form.value.photos.length
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

// 小程序端把本地图片转 base64——因为后端 AI（豆包）没法直接访问微信的临时文件URL。
// 微信文件系统读出来就是 base64，不用额外编码。
// H5 环境走 canvas 方案，质量设 0.8 是在清晰度和传输大小之间的折中。
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
    // H5环境用canvas转base64
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

async function analyzeHazard() {
  if (form.value.photos.length === 0) {
    uni.showToast({ title: '请先上传照片', icon: 'none' })
    return
  }

  analyzing.value = true
  uni.showLoading({ title: 'AI分析中...' })

  try {
    // 转 base64 再发给 AI——折腾这一道是因为微信小程序的临时文件路径
    // 是 wxfile:// 开头的本地路径，服务器根本访问不了
    const base64Photos: string[] = []
    for (const path of form.value.photos) {
      const b64 = await photoToBase64(path)
      base64Photos.push(b64)
    }

    const result = await api.analyzeHazard({
      description: form.value.description,
      photos: base64Photos
    })

    aiResult.value = {
      ...result,
      hazard_type_name: typeMap[result.hazard_type] || result.hazard_type
    }

    // AI 返回结果自动回填表单，省得用户手动选。
    // 但 AI 也可能判错，所以用户还能手动改，不做 lock。
    if (result.hazard_type) {
      form.value.hazard_type = result.hazard_type
      typeIndex.value = typeOptions.findIndex(t => t.value === result.hazard_type)
    }
    if (result.level) {
      form.value.level = result.level
    }

    uni.hideLoading()
    uni.showToast({ title: 'AI分析完成', icon: 'success' })
  } catch (error: any) {
    uni.hideLoading()
    const msg = error?.message || 'AI分析失败，请手动填写'
    uni.showToast({ title: msg, icon: 'none' })
    console.error('AI分析失败:', error)
  } finally {
    analyzing.value = false
  }
}

async function submitHazard() {
  if (!form.value.title) {
    uni.showToast({ title: '请输入隐患标题', icon: 'none' })
    return
  }
  if (!form.value.hazard_type) {
    uni.showToast({ title: '请选择隐患类型', icon: 'none' })
    return
  }
  if (!form.value.location) {
    uni.showToast({ title: '请输入隐患位置', icon: 'none' })
    return
  }
  if (!form.value.description) {
    uni.showToast({ title: '请描述隐患情况', icon: 'none' })
    return
  }
  if (form.value.photos.length === 0) {
    uni.showToast({ title: '请上传现场照片', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    // 先上传图片拿到 URL，再提交表单。之前试过图省事把 base64 直接塞给后端，
    // 结果一张图 2MB，三张图直接超时。现在老老实实先传图。
    uni.showLoading({ title: '上传中...' })
    const uploadedUrls = await uploadImages(form.value.photos)
    uni.hideLoading()

    if (uploadedUrls.length === 0) {
      uni.showToast({ title: '图片上传失败', icon: 'none' })
      submitting.value = false
      return
    }

    await api.createHazard({
      title: form.value.title,
      hazard_type: form.value.hazard_type,
      level: form.value.level,
      location: form.value.location,
      description: form.value.description,
      photos: uploadedUrls,
      ai_tags: aiResult.value?.tags || [],
      ai_analysis: aiResult.value?.analysis || '',
      ai_hazard_type: aiResult.value?.hazard_type || '',
      ai_level: aiResult.value?.level || ''
    })
    requestSubscribe(['hazard_new', 'rectify_result'])
    uni.showToast({ title: '上报成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error: any) {
    uni.hideLoading()
    uni.showToast({ title: error.message || '上报失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
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

/* Form Container */
.form-container {
  padding: 24rpx 32rpx 48rpx;
  margin-top: -24rpx;
  position: relative;
}

/* Form Card */
.form-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.form-item {
  margin-bottom: 16rpx;
}

.form-item:last-child {
  margin-bottom: 0;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 4rpx;
  margin-bottom: 16rpx;
}

.item-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #0f172a;
}

.item-required {
  font-size: 28rpx;
  color: #f43f5e;
}

.item-hint {
  display: block;
  font-size: 28rpx;
  color: #64748b;
  margin-bottom: 16rpx;
}

/* Input & Picker */
.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 20rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #0f172a;
}

.input-placeholder {
  color: #64748b;
}

.form-picker {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 88rpx;
  padding: 0 20rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #0f172a;
}

.picker-placeholder {
  color: #64748b;
}

.picker-arrow {
  font-size: 24rpx;
  color: #64748b;
}

/* Divider */
.form-divider {
  height: 1rpx;
  background: #f1f5f9;
  margin: 20rpx 0;
}

/* Level Options */
.level-options {
  display: flex;
  gap: 16rpx;
}

.level-option {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 16rpx;
  transition: all 0.2s ease;
}

.level-option.active {
  background: #f0fdfa;
  border-color: #06b6d4;
}

.level-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
}

.level-icon--warning {
  background: #fef3c7;
  color: #b45309;
}

.level-icon--danger {
  background: #fee2e2;
  color: #dc2626;
}

.level-info {
  display: flex;
  flex-direction: column;
}

.level-label {
  font-size: 26rpx;
  font-weight: 600;
  color: #0f172a;
}

.level-desc {
  font-size: 26rpx;
  color: #64748b;
}

/* Textarea */
.form-textarea {
  width: 100%;
  height: 240rpx;
  padding: 20rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #0f172a;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 26rpx;
  color: #64748b;
  margin-top: 8rpx;
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
  margin-bottom: 4rpx;
}

.add-text {
  font-size: 28rpx;
  color: #64748b;
}

.add-count {
  font-size: 24rpx;
  color: #64748b;
  margin-top: 4rpx;
}

/* AI Analyze Button */
.btn-analyze {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #ffffff;
  border: none;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  margin-top: 16rpx;
  box-shadow: 0 8rpx 24rpx rgba(99, 102, 241, 0.25);
}

.btn-analyze:disabled {
  opacity: 0.5;
}

/* AI Result Card */
.ai-result-card {
  border: 2rpx solid #6366f1;
  background: #fafafe;
}

.ai-result-header {
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
  padding: 12rpx 0;
}

.ai-result-label {
  font-size: 26rpx;
  color: #64748b;
  width: 140rpx;
  flex-shrink: 0;
}

.ai-result-value {
  font-size: 26rpx;
  font-weight: 600;
  color: #0f172a;
}

.text-danger {
  color: #dc2626;
}

.text-warning {
  color: #b45309;
}

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
  padding-top: 16rpx;
}

.ai-analysis-text {
  display: block;
  font-size: 28rpx;
  color: #475569;
  margin-top: 8rpx;
  line-height: 1.6;
}

/* Submit Section */
.submit-section {
  padding-top: 16rpx;
}

.btn-submit {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
  color: #ffffff;
  border: none;
  border-radius: 20rpx;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: 0 12rpx 32rpx rgba(244, 63, 94, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
}

.submit-hint {
  display: block;
  text-align: center;
  font-size: 28rpx;
  color: #64748b;
  margin-top: 16rpx;
}
</style>
