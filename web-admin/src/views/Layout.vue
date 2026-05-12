<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getUnreadCount } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)

const menuItems = [
  { path: '/dashboard', icon: 'DataAnalysis', title: '数据监控', color: '#06b6d4' },
  { path: '/users', icon: 'User', title: '用户管理', color: '#8b5cf6' },
  { path: '/areas', icon: 'OfficeBuilding', title: '区域管理', color: '#f59e0b' },
  { path: '/points', icon: 'Location', title: '点位管理', color: '#10b981' },
  { path: '/records', icon: 'Document', title: '巡检记录', color: '#3b82f6' },
  { path: '/hazards', icon: 'Warning', title: '隐患管理', color: '#ef4444' },
  { path: '/tasks', icon: 'CircleCheck', title: '整改任务', color: '#06b6d4' },
  { path: '/logs', icon: 'Clock', title: '操作日志', color: '#6b7280' },
  { path: '/notifications', icon: 'Bell', title: '消息推送', color: '#f59e0b' }
]

const roleMap = {
  admin: '超级管理员',
  safety_manager: '安全管理员',
  inspector: '巡检员',
  rectifier: '整改负责人'
}

const userRole = computed(() => roleMap[userStore.user?.role] || '用户')
const unreadCount = ref(0)
let unreadTimer = null

onMounted(() => {
  fetchUnreadCount()
  unreadTimer = setInterval(fetchUnreadCount, 30000)
})

onUnmounted(() => {
  if (unreadTimer) clearInterval(unreadTimer)
})

async function fetchUnreadCount() {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data.total_unread || 0
  } catch (e) {
    // 未读数拉取失败就保持上次的显示，不用弹错误提示干扰用户
  }
}

function goNotifications() {
  router.push('/notifications')
}

function handleCommand(command) {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
      confirmButtonText: '确定退出',
      cancelButtonText: '取消',
      type: 'warning',
      customClass: 'logout-dialog'
    }).then(() => {
      userStore.logout()
      router.push('/login')
    }).catch(() => {})
  }
}
</script>

<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '72px' : '240px'" class="sidebar">
      <!-- Logo Area -->
      <div class="sidebar-header" :class="{ collapsed: isCollapse }">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 22V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 7L12 12L3 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.3"/>
          </svg>
        </div>
        <transition name="fade">
          <div v-if="!isCollapse" class="logo-text">
            <span class="logo-title">校园安全</span>
            <span class="logo-subtitle">管理平台</span>
          </div>
        </transition>
      </div>

      <!-- Navigation Menu -->
      <nav class="sidebar-nav">
        <router-link
          v-for="(item, index) in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
          :style="{ '--item-color': item.color, '--delay': `${index * 50}ms` }"
        >
          <div class="nav-icon-wrapper">
            <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
          </div>
          <transition name="fade">
            <span v-if="!isCollapse" class="nav-title">{{ item.title }}</span>
          </transition>
          <div v-if="route.path === item.path && !isCollapse" class="active-indicator"></div>
        </router-link>
      </nav>

      <!-- Sidebar Footer -->
      <div class="sidebar-footer" v-if="!isCollapse">
        <div class="version-info">
          <span class="version-label">Version</span>
          <span class="version-number">1.0.0</span>
        </div>
      </div>
    </el-aside>

    <!-- Main Content Area -->
    <el-container class="main-container">
      <!-- Header -->
      <el-header class="header">
        <div class="header-left">
          <button class="collapse-btn" @click="isCollapse = !isCollapse">
            <el-icon :size="18">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </button>
          <div class="breadcrumb">
            <span class="breadcrumb-item">{{ menuItems.find(m => m.path === route.path)?.title || '首页' }}</span>
          </div>
        </div>

        <div class="header-right">
          <!-- Notifications -->
          <button class="header-btn notification-btn" @click="goNotifications">
            <el-icon :size="20"><Bell /></el-icon>
            <span class="notification-dot" v-if="unreadCount > 0"></span>
            <span class="notification-badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
          </button>

          <!-- User Dropdown -->
          <el-dropdown @command="handleCommand" trigger="click" class="user-dropdown">
            <div class="user-info">
              <div class="user-avatar">
                <span>{{ userStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}</span>
              </div>
              <div class="user-details">
                <span class="user-name">{{ userStore.user?.username || '用户' }}</span>
                <span class="user-role">{{ userRole }}</span>
              </div>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown-menu">
                <div class="dropdown-header">
                  <span class="dropdown-username">{{ userStore.user?.username }}</span>
                  <span class="dropdown-email">{{ userStore.user?.email || 'admin@campus.edu' }}</span>
                </div>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  <span>系统设置</span>
                </el-dropdown-item>
                <el-dropdown-item divided command="logout" class="logout-item">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Main Content -->
      <el-main class="main-content">
        <RouterView v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
/* ========================================
   Layout Container
   ======================================== */
.layout-container {
  height: 100vh;
  overflow: hidden;
}

.main-container {
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

/* ========================================
   Sidebar Styles
   ======================================== */
.sidebar {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
}

/* Sidebar Header / Logo */
.sidebar-header {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.2);
}

.sidebar-header.collapsed {
  justify-content: center;
  padding: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #22d3ee;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.logo-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.logo-subtitle {
  font-size: 11px;
  color: #94a3b8;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Navigation Menu */
.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 10px;
  text-decoration: none;
  color: #94a3b8;
  position: relative;
  transition: all 0.2s ease;
  animation: slideInLeft 0.3s ease-out backwards;
  animation-delay: var(--delay);
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
}

.nav-item.active {
  background: rgba(6, 182, 212, 0.15);
  color: #ffffff;
}

.nav-item.active .nav-icon-wrapper {
  color: var(--item-color);
}

.nav-item.active .nav-icon-wrapper::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--item-color);
  opacity: 0.15;
  border-radius: 8px;
}

.nav-icon-wrapper {
  position: relative;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.nav-icon {
  font-size: 18px;
}

.nav-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  letter-spacing: 0.2px;
}

.active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: var(--item-color);
  border-radius: 0 3px 3px 0;
  box-shadow: 0 0 10px var(--item-color);
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.version-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.version-label {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.version-number {
  font-size: 11px;
  color: #22d3ee;
  font-family: 'JetBrains Mono', monospace;
}

/* ========================================
   Header Styles
   ======================================== */
.header {
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background: #e2e8f0;
  color: #334155;
  border-color: #cbd5e1;
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb-item {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 10px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.header-btn:hover {
  background: #f1f5f9;
  color: #334155;
}

.notification-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid #ffffff;
}

.notification-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #ef4444;
  color: #ffffff;
  font-size: 10px;
  font-weight: 600;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #ffffff;
  line-height: 1;
}

/* User Dropdown */
.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  border-radius: 12px;
  transition: background 0.2s ease;
}

.user-info:hover {
  background: #f8fafc;
}

.user-avatar {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  border-radius: 10px;
  color: white;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 15px;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(6, 182, 212, 0.3);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.user-role {
  font-size: 11px;
  color: #64748b;
}

.dropdown-arrow {
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.user-dropdown:focus-within .dropdown-arrow {
  transform: rotate(180deg);
}

/* ========================================
   Main Content Area
   ======================================== */
.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f8fafc;
}

/* ========================================
   Transitions
   ======================================== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-enter-active,
.page-leave-active {
  transition: all 0.25s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ========================================
   Dropdown Menu Styles (Deep)
   ======================================== */
:deep(.user-dropdown-menu) {
  padding: 8px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  min-width: 200px;
}

:deep(.dropdown-header) {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 8px;
}

:deep(.dropdown-username) {
  display: block;
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

:deep(.dropdown-email) {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  transition: all 0.15s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f8fafc;
  color: #1e293b;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
  color: #94a3b8;
}

:deep(.logout-item) {
  color: #ef4444;
}

:deep(.logout-item .el-icon) {
  color: #ef4444;
}

:deep(.logout-item:hover) {
  background: #fef2f2;
  color: #dc2626;
}

/* ========================================
   Logout Dialog Styles
   ======================================== */
:deep(.logout-dialog) {
  border-radius: 16px;
  padding: 24px;
}
</style>
