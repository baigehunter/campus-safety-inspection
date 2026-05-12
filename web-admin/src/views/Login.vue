<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await userStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    const detail = error.response?.data?.detail
      || error.response?.data?.non_field_errors?.[0]
    if (detail) {
      ElMessage.error(detail)
    } else if (error.response?.status === 400) {
      ElMessage.error('请求被服务器拒绝(400)。请检查服务器 ALLOWED_HOSTS 配置是否包含当前域名。')
    } else if (!error.response) {
      ElMessage.error('无法连接服务器，请检查网络或服务器是否启动。')
    } else {
      ElMessage.error(`服务器错误(${error.response.status})，请检查服务器配置。`)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <!-- Background Pattern -->
    <div class="bg-pattern"></div>

    <!-- Floating Elements -->
    <div class="floating-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
    </div>

    <!-- Login Card -->
    <div class="login-wrapper">
      <div class="login-card">
        <!-- Left Side - Branding -->
        <div class="login-brand">
          <div class="brand-content">
            <div class="brand-icon">
              <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M24 4L6 14V34L24 44L42 34V14L24 4Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M24 44V24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M42 14L24 24L6 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="24" cy="24" r="6" fill="currentColor" opacity="0.3"/>
              </svg>
            </div>
            <h1 class="brand-title">校园安全管理平台</h1>
            <p class="brand-subtitle">Campus Safety Management System</p>

            <div class="features">
              <div class="feature-item">
                <div class="feature-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 12l2 2 4-4"/>
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                </div>
                <span>实时巡检管理</span>
              </div>
              <div class="feature-item">
                <div class="feature-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 12l2 2 4-4"/>
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                </div>
                <span>隐患闭环处理</span>
              </div>
              <div class="feature-item">
                <div class="feature-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 12l2 2 4-4"/>
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                </div>
                <span>数据可视化分析</span>
              </div>
            </div>
          </div>

          <!-- Decorative Elements -->
          <div class="brand-decoration">
            <div class="decoration-circle circle-1"></div>
            <div class="decoration-circle circle-2"></div>
            <div class="decoration-circle circle-3"></div>
          </div>
        </div>

        <!-- Right Side - Login Form -->
        <div class="login-form-wrapper">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录您的账户以继续</p>
          </div>

          <form class="login-form" @submit.prevent="handleLogin">
            <div class="input-group">
              <label class="input-label">用户名</label>
              <div class="input-wrapper">
                <el-icon class="input-icon"><User /></el-icon>
                <input
                  v-model="form.username"
                  type="text"
                  class="input-field"
                  placeholder="请输入用户名"
                  autocomplete="username"
                />
              </div>
            </div>

            <div class="input-group">
              <label class="input-label">密码</label>
              <div class="input-wrapper">
                <el-icon class="input-icon"><Lock /></el-icon>
                <input
                  v-model="form.password"
                  type="password"
                  class="input-field"
                  placeholder="请输入密码"
                  autocomplete="current-password"
                />
              </div>
            </div>

            <div class="form-options">
              <label class="remember-me">
                <input type="checkbox" />
                <span class="checkmark"></span>
                <span>记住我</span>
              </label>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>

            <button type="submit" class="submit-btn" :class="{ loading }" :disabled="loading">
              <span v-if="!loading">登 录</span>
              <span v-else class="loading-spinner"></span>
            </button>
          </form>

          <div class="form-footer">
            <p>© 2024 校园安全管理平台 · 安全守护每一天</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ========================================
   Login Container
   ======================================== */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  position: relative;
  overflow: hidden;
}

/* Background Pattern */
.bg-pattern {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 80%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

/* Floating Shapes */
.floating-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  bottom: 10%;
  left: 10%;
  animation-delay: -5s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  top: 20%;
  right: 5%;
  animation-delay: -10s;
}

.shape-4 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #10b981, #059669);
  bottom: -50px;
  right: -50px;
  animation-delay: -15s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(20px, -20px) rotate(5deg); }
  50% { transform: translate(-10px, 20px) rotate(-5deg); }
  75% { transform: translate(-20px, -10px) rotate(3deg); }
}

/* ========================================
   Login Card
   ======================================== */
.login-wrapper {
  position: relative;
  z-index: 1;
  padding: 20px;
  width: 100%;
  max-width: 1000px;
}

.login-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

@media (max-width: 768px) {
  .login-card {
    grid-template-columns: 1fr;
  }

  .login-brand {
    display: none;
  }
}

/* ========================================
   Brand Section
   ======================================== */
.login-brand {
  padding: 48px;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.brand-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  color: #22d3ee;
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    filter: drop-shadow(0 0 20px rgba(34, 211, 238, 0.5));
  }
  50% {
    filter: drop-shadow(0 0 40px rgba(34, 211, 238, 0.8));
  }
}

.brand-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.brand-subtitle {
  font-size: 14px;
  color: #94a3b8;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 40px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #e2e8f0;
  font-size: 14px;
}

.feature-icon {
  width: 24px;
  height: 24px;
  color: #22d3ee;
}

/* Brand Decoration */
.brand-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -50px;
  right: -50px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -100px;
  left: -100px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* ========================================
   Form Section
   ======================================== */
.login-form-wrapper {
  padding: 48px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header {
  margin-bottom: 32px;
}

.form-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 14px;
  color: #64748b;
}

/* Input Fields */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  letter-spacing: 0.3px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  color: #94a3b8;
  font-size: 18px;
  z-index: 1;
  transition: color 0.2s ease;
}

.input-field {
  width: 100%;
  padding: 14px 16px 14px 48px;
  font-family: 'Inter', 'PingFang SC', sans-serif;
  font-size: 15px;
  color: #0f172a;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.input-field::placeholder {
  color: #94a3b8;
}

.input-field:focus {
  outline: none;
  background: #ffffff;
  border-color: #06b6d4;
  box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.1);
}

.input-field:focus + .input-icon,
.input-wrapper:focus-within .input-icon {
  color: #06b6d4;
}

/* Form Options */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
}

.remember-me input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 5px;
  transition: all 0.2s ease;
  position: relative;
}

.remember-me input:checked + .checkmark {
  background: #06b6d4;
  border-color: #06b6d4;
}

.remember-me input:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.forgot-link {
  font-size: 13px;
  color: #06b6d4;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.forgot-link:hover {
  color: #0891b2;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  padding: 16px;
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  letter-spacing: 2px;
}

.submit-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.submit-btn:hover::before {
  opacity: 1;
}

.submit-btn span {
  position: relative;
  z-index: 1;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(6, 182, 212, 0.3);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn.loading {
  pointer-events: none;
  opacity: 0.8;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Form Footer */
.form-footer {
  margin-top: 32px;
  text-align: center;
}

.form-footer p {
  font-size: 12px;
  color: #94a3b8;
}
</style>
