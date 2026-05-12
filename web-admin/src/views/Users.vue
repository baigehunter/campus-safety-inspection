<script setup>
import { ref, onMounted, computed } from 'vue'
import { getUsers, createUser, updateUser, disableUser, deleteUser, resetPassword } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 10 })
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({})
const submitting = ref(false)

// 当前登录用户信息
const currentUser = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
})

const roleOptions = [
  { value: 'admin', label: '超级管理员', color: '#8b5cf6' },
  { value: 'safety_manager', label: '安全管理员', color: '#06b6d4' },
  { value: 'inspector', label: '巡检员', color: '#10b981' },
  { value: 'rectifier', label: '整改负责人', color: '#f59e0b' }
]

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  try {
    const res = await getUsers(query.value)
    tableData.value = res.data.results || res.data
    total.value = res.data.count || tableData.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  form.value = { role: 'inspector' }
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
}

function handleEdit(row) {
  form.value = { ...row }
  dialogTitle.value = '编辑用户'
  dialogVisible.value = true
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (form.value.id) {
      await updateUser(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createUser(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

function handleDisable(row) {
  // 防止把自己给禁了——真禁了就再也登不进去了，只能去数据库改
  if (currentUser.value && row.id === currentUser.value.id) {
    ElMessage.warning('不能禁用自己的账号')
    return
  }

  ElMessageBox.confirm(
    `确定要禁用用户「${row.username}」吗？禁用后该用户将无法登录系统。`,
    '禁用用户',
    {
      confirmButtonText: '确定禁用',
      cancelButtonText: '取消',
      type: 'warning',
      customClass: 'confirm-dialog'
    }
  ).then(async () => {
    try {
      await disableUser(row.id)
      ElMessage.success('已禁用该用户')
      fetchData()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '操作失败')
    }
  }).catch(() => {})
}

function handleDelete(row) {
  // 不能删除自己
  if (currentUser.value && row.id === currentUser.value.id) {
    ElMessage.warning('不能删除自己的账号')
    return
  }
  // 不能删除超级管理员
  if (row.role === 'admin') {
    ElMessage.warning('不能删除超级管理员账号')
    return
  }

  ElMessageBox.confirm(
    `确定要删除用户「${row.username}」吗？此操作不可恢复。`,
    '删除用户',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      customClass: 'confirm-dialog',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }).catch(() => {})
}

function handleResetPassword(row) {
  ElMessageBox.prompt('请输入新密码', `重置「${row.username}」的密码`, {
    confirmButtonText: '确定重置',
    cancelButtonText: '取消',
    inputPattern: /.{6,}/,
    inputErrorMessage: '密码长度至少6位',
    inputPlaceholder: '请输入新密码（至少6位）',
    customClass: 'reset-password-dialog'
  }).then(async ({ value }) => {
    try {
      await resetPassword({ user_id: row.id, new_password: value })
      ElMessage.success('密码重置成功')
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

function handleCommand(command, row) {
  switch (command) {
    case 'edit':
      handleEdit(row)
      break
    case 'reset':
      handleResetPassword(row)
      break
    case 'disable':
      handleDisable(row)
      break
    case 'delete':
      handleDelete(row)
      break
  }
}

// 检查是否可以删除用户（仅超级管理员）
function canDeleteUser(row) {
  if (currentUser.value?.role !== 'admin') return false
  if (currentUser.value && row.id === currentUser.value.id) return false
  if (row.role === 'admin') return false
  return true
}

// 检查是否可以禁用用户
function canDisableUser(row) {
  if (currentUser.value && row.id === currentUser.value.id) return false
  return true
}

function getRoleConfig(role) {
  const config = roleOptions.find(r => r.value === role)
  return config || { label: '未知', color: '#6b7280' }
}
</script>

<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理系统用户账号和权限</p>
      </div>
      <button class="add-btn" @click="handleAdd">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>新增用户</span>
      </button>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <el-table :data="tableData" v-loading="loading" class="data-table">
        <!-- User Info Column -->
        <el-table-column label="用户信息" min-width="200">
          <template #default="{ row }">
            <div class="user-info">
              <div class="user-avatar" :style="{ background: getRoleConfig(row.role).color }">
                {{ row.username?.charAt(0)?.toUpperCase() || 'U' }}
              </div>
              <div class="user-details">
                <span class="user-name">{{ row.username }}</span>
                <span class="user-email">{{ row.email || '未设置邮箱' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Role Column -->
        <el-table-column prop="role_name" label="角色" width="150">
          <template #default="{ row }">
            <span class="role-badge" :style="{ '--role-color': getRoleConfig(row.role).color }">
              {{ row.role_name }}
            </span>
          </template>
        </el-table-column>

        <!-- Phone Column -->
        <el-table-column prop="phone" label="手机号" width="150">
          <template #default="{ row }">
            <span class="phone-text">{{ row.phone || '-' }}</span>
          </template>
        </el-table-column>

        <!-- Status Column -->
        <el-table-column prop="is_active" label="状态" width="120">
          <template #default="{ row }">
            <span class="status-badge" :class="row.is_active ? 'status--active' : 'status--inactive'">
              <span class="status-dot"></span>
              {{ row.is_active ? '启用' : '禁用' }}
            </span>
          </template>
        </el-table-column>

        <!-- Actions Column -->
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
              <button class="action-trigger">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="6" r="2"/>
                  <circle cx="12" cy="12" r="2"/>
                  <circle cx="12" cy="18" r="2"/>
                </svg>
              </button>
              <template #dropdown>
                <el-dropdown-menu class="action-menu">
                  <el-dropdown-item command="edit" class="action-item action-item--edit">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    <span>编辑信息</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="reset" class="action-item action-item--reset">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                    <span>重置密码</span>
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="canDisableUser(row)"
                    command="disable"
                    class="action-item action-item--warning"
                    divided
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
                    </svg>
                    <span>禁用用户</span>
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="canDeleteUser(row)"
                    command="delete"
                    class="action-item action-item--danger"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                    <span>删除用户</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Pagination -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="query.page"
        :page-size="query.page_size"
        :total="total"
        @current-change="fetchData"
        layout="total, prev, pager, next"
        background
      />
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="480px"
      class="user-dialog"
      destroy-on-close
    >
      <el-form :model="form" label-position="top" class="user-form">
        <el-form-item label="用户名" required>
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="!!form.id"
            class="form-input"
          />
        </el-form-item>
        <el-form-item label="密码" required v-if="!form.id">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            show-password
            class="form-input"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱地址"
            class="form-input"
          />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="form.role" placeholder="请选择角色" class="form-select">
            <el-option
              v-for="opt in roleOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            >
              <div class="role-option">
                <span class="role-dot" :style="{ background: opt.color }"></span>
                <span>{{ opt.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            class="form-input"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn--ghost" @click="dialogVisible = false">取消</button>
          <button class="btn btn--primary" @click="handleSubmit" :disabled="submitting">
            {{ submitting ? '提交中...' : '确定' }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* ========================================
   Page Container
   ======================================== */
.page-container {
  min-height: 100%;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.5px;
  margin: 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.3);
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(6, 182, 212, 0.4);
}

.add-btn svg {
  width: 18px;
  height: 18px;
}

/* ========================================
   Table Styles
   ======================================== */
.table-wrapper {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  overflow: hidden;
}

.data-table {
  --el-table-border-color: #f1f5f9;
  --el-table-header-bg-color: #f8fafc;
  --el-table-header-text-color: #334155;
  --el-table-row-hover-bg-color: #f8fafc;
  --el-table-text-color: #475569;
}

:deep(.el-table__header th) {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 16px 12px;
}

:deep(.el-table__body td) {
  padding: 16px 12px;
}

/* User Info Cell */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  color: #0f172a;
  font-size: 14px;
}

.user-email {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Role Badge */
.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: color-mix(in srgb, var(--role-color) 15%, transparent);
  color: var(--role-color);
  border: 1px solid color-mix(in srgb, var(--role-color) 30%, transparent);
}

/* Phone Text */
.phone-text {
  font-size: 13px;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.status--active {
  background: #d1fae5;
  color: #059669;
}

.status-badge.status--active .status-dot {
  background: #10b981;
  box-shadow: 0 0 6px #10b981;
}

.status-badge.status--inactive {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.status--inactive .status-dot {
  background: #ef4444;
}

/* ========================================
   Action Button & Dropdown
   ======================================== */
.action-trigger {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-trigger:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #334155;
}

.action-trigger svg {
  width: 16px;
  height: 16px;
}

/* Dropdown Menu */
:deep(.action-menu) {
  padding: 8px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  min-width: 160px;
}

:deep(.action-item) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  transition: all 0.15s ease;
}

:deep(.action-item svg) {
  width: 16px;
  height: 16px;
}

:deep(.action-item:hover) {
  background: #f8fafc;
}

:deep(.action-item--edit:hover) {
  background: #f0f9ff;
  color: #0284c7;
}

:deep(.action-item--reset:hover) {
  background: #fefce8;
  color: #ca8a04;
}

:deep(.action-item--warning) {
  color: #d97706;
}

:deep(.action-item--warning:hover) {
  background: #fffbeb;
  color: #b45309;
}

:deep(.action-item--danger) {
  color: #dc2626;
}

:deep(.action-item--danger:hover) {
  background: #fef2f2;
  color: #dc2626;
}

/* ========================================
   Pagination
   ======================================== */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: #0f172a;
}

/* ========================================
   Dialog Styles
   ======================================== */
:deep(.user-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.user-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  margin: 0;
}

:deep(.user-dialog .el-dialog__title) {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-weight: 600;
  font-size: 18px;
  color: #0f172a;
}

:deep(.user-dialog .el-dialog__body) {
  padding: 24px;
}

.user-form :deep(.el-form-item__label) {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-weight: 600;
  color: #334155;
  font-size: 13px;
  padding-bottom: 8px;
}

.form-input,
.form-select {
  width: 100%;
}

:deep(.form-input .el-input__wrapper),
:deep(.form-select .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
  padding: 4px 12px;
}

:deep(.form-input .el-input__wrapper:focus-within),
:deep(.form-select .el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2), 0 0 0 1px #06b6d4;
}

.role-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border-radius: 10px;
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn--ghost {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn--ghost:hover {
  background: #f8fafc;
  color: #334155;
}

.btn--primary {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: white;
}

.btn--primary:hover {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
}

.btn--primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ========================================
   Confirm Dialog
   ======================================== */
:deep(.confirm-dialog),
:deep(.reset-password-dialog) {
  border-radius: 16px;
}

:deep(.confirm-dialog .el-message-box__header),
:deep(.reset-password-dialog .el-message-box__header) {
  padding-top: 20px;
}

:deep(.confirm-dialog .el-message-box__title),
:deep(.reset-password-dialog .el-message-box__title) {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-weight: 600;
}
</style>
