<template>
  <view class="page">
    <view class="bg-decor">
      <view class="bg-circle bg-circle--1" :class="{ 'anim-drift': pageReady }"></view>
      <view class="bg-circle bg-circle--2" :class="{ 'anim-drift': pageReady }"></view>
      <view class="bg-circle bg-circle--3" :class="{ 'anim-drift': pageReady }"></view>
    </view>

    <view class="content">
      <view class="logo-section anim-fade-up">
        <view class="logo-mark">
          <text class="logo-symbol">安</text>
        </view>
        <text class="brand-name">校园安全巡检</text>
        <text class="brand-desc">Campus Safety Inspection</text>
      </view>

      <!-- Login Panel -->
      <view class="login-panel anim-fade-up delay-2">
        <view class="panel-head">
          <text class="panel-title">账号登录</text>
          <text class="panel-sub">请使用分配的账号登录系统</text>
        </view>

        <view class="form">
          <!-- Username -->
          <view class="field anim-fade-up delay-3">
            <text class="field-label">用户名</text>
            <view class="input-wrap">
              <text class="input-icon">👤</text>
              <input
                class="input"
                v-model="form.username"
                placeholder="请输入用户名"
                placeholder-class="input-ph"
              />
            </view>
          </view>

          <!-- Password -->
          <view class="field anim-fade-up delay-4">
            <text class="field-label">密码</text>
            <view class="input-wrap">
              <text class="input-icon">🔒</text>
              <input
                class="input"
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                placeholder-class="input-ph"
              />
            </view>
          </view>

          <!-- Login Button -->
          <button
            class="login-btn anim-fade-up delay-5"
            @click="handleLogin"
            :disabled="loading"
            :loading="loading"
          >
            <text v-if="!loading">登 录</text>
            <text v-else>验证中...</text>
          </button>
        </view>

        <view class="panel-foot">
          <text>如遇登录问题，请联系系统管理员</text>
        </view>
      </view>

      <!-- Footer -->
      <view class="footer anim-fade-in delay-5">
        <text>校园安全监控系统 v2.0</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { api } from '@/utils/request'

const form = ref({ username: '', password: '' })
const loading = ref(false)
const pageReady = ref(false)

onMounted(() => {
  nextTick(() => { pageReady.value = true })
})

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res: any = await api.login(form.value)
    uni.setStorageSync('access_token', res.access)
    uni.setStorageSync('refresh_token', res.refresh)
    uni.setStorageSync('userInfo', res.user)

    // —— 上传微信 OpenID，用于后续订阅消息推送 ——
    // 这里注意：OpenID 不是登录必需的，上传失败不能影响用户登录，
    // 否则网络波动时用户会卡在登录页，体验很差。之前踩过这个坑。
    // #ifdef MP-WEIXIN
    try {
      const loginRes: any = await new Promise((resolve, reject) => {
        uni.login({ success: resolve, fail: reject })
      })
      if (loginRes.code) {
        await api.getOpenId(loginRes.code)
      }
    } catch (e) {
      // 静默失败，不影响登录流程
      console.error('获取 openid 失败:', e)
    }
    // #endif

    uni.showToast({ title: '登录成功', icon: 'success' })
    // 延迟 800ms 再跳转——让用户看到"登录成功"的 toast，
    // 太快跳转 toast 一闪而过用户根本不知道发生了什么
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/index/index' })
    }, 800)
  } catch (error: any) {
    uni.showToast({ title: error.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(160deg, #f0f4ff 0%, #f8fafc 30%, #f0f9ff 70%, #f5f3ff 100%);
  overflow: hidden;
}

/* Background decoration */
.bg-decor {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.4;
}

.bg-circle--1 {
  width: 600rpx;
  height: 600rpx;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.06) 0%, transparent 70%);
  top: -200rpx;
  right: -150rpx;
}

.bg-circle--2 {
  width: 500rpx;
  height: 500rpx;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.05) 0%, transparent 70%);
  bottom: -100rpx;
  left: -180rpx;
}

.bg-circle--3 {
  width: 300rpx;
  height: 300rpx;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.04) 0%, transparent 70%);
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Content */
.content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 48rpx 60rpx;
  box-sizing: border-box;
}

/* Logo */
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 64rpx;
}

.logo-mark {
  width: 120rpx;
  height: 120rpx;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28rpx;
  box-shadow: 0 16rpx 40rpx rgba(37, 99, 235, 0.2);
}

.logo-symbol {
  font-size: 52rpx;
  font-weight: 800;
  color: #ffffff;
}

.brand-name {
  font-size: 38rpx;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: 4rpx;
  margin-bottom: 10rpx;
}

.brand-desc {
  font-size: 28rpx;
  color: #64748b;
  letter-spacing: 2rpx;
  text-transform: uppercase;
}

/* Login Panel */
.login-panel {
  width: 100%;
  max-width: 600rpx;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 44rpx 36rpx 36rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04), 0 1rpx 4rpx rgba(0, 0, 0, 0.02);
}

.panel-head {
  margin-bottom: 36rpx;
}

.panel-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8rpx;
}

.panel-sub {
  display: block;
  font-size: 26rpx;
  color: #64748b;
}

/* Form */
.form {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.field-label {
  font-size: 26rpx;
  font-weight: 600;
  color: #475569;
}

.input-wrap {
  display: flex;
  align-items: center;
  height: 96rpx;
  padding: 0 20rpx;
  background: #f8fafc;
  border: 2rpx solid #e8ecf1;
  border-radius: 16rpx;
  gap: 14rpx;
  transition: border-color 0.2s;
}

.input-wrap:focus-within {
  border-color: #2563eb;
  background: #ffffff;
}

.input-icon {
  font-size: 32rpx;
}

.input {
  flex: 1;
  height: 96rpx;
  font-size: 30rpx;
  color: #1e293b;
  background: transparent;
}

.input-ph {
  color: #b0b8c4;
  font-size: 28rpx;
}

/* Login Button */
.login-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border: none;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
  margin-top: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 32rpx rgba(37, 99, 235, 0.25);
  transition: all 0.2s ease;
}

.login-btn:active {
  transform: scale(0.98);
  box-shadow: 0 8rpx 20rpx rgba(37, 99, 235, 0.2);
}

.login-btn[disabled] {
  opacity: 0.6;
}

/* Panel Footer */
.panel-foot {
  margin-top: 32rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #f1f5f9;
  text-align: center;
}

.panel-foot text {
  font-size: 28rpx;
  color: #64748b;
}

/* Footer */
.footer {
  margin-top: auto;
  padding-top: 48rpx;
}

.footer text {
  font-size: 26rpx;
  color: #64748b;
}
</style>
