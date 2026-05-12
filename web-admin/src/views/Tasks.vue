<script setup>
import { ref, onMounted } from 'vue'
import { getTasks, reviewTask } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const query = ref({ page: 1, page_size: 10, status: '', total: 0 })
const dialogVisible = ref(false)
const reviewForm = ref({})

const statusOptions = [
  { value: 'pending', label: '待整改', color: '#64748b' },
  { value: 'processing', label: '整改中', color: '#f59e0b' },
  { value: 'submitted', label: '待验收', color: '#3b82f6' },
  { value: 'completed', label: '已完成', color: '#10b981' },
  { value: 'rejected', label: '已驳回', color: '#ef4444' }
]

onMounted(fetchData)

async function fetchData() {
  loading.value = true
  try {
    const res = await getTasks(query.value)
    tableData.value = res.data.results || res.data
    query.value.total = res.data.count || tableData.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleReview(row) {
  reviewForm.value = { task_id: row.id, result: '', remark: '' }
  dialogVisible.value = true
}

async function handleSubmitReview() {
  if (!reviewForm.value.result) {
    ElMessage.warning('请选择验收结果')
    return
  }
  try {
    await reviewTask(reviewForm.value.task_id, {
      result: reviewForm.value.result,
      remark: reviewForm.value.remark
    })
    ElMessage.success('验收完成')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('验收失败')
  }
}

function getStatusConfig(status) {
  const config = statusOptions.find(s => s.value === status)
  return config || { label: status, color: '#64748b' }
}
</script>

<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">整改任务管理</h1>
        <p class="page-subtitle">跟踪和管理隐患整改任务</p>
      </div>
      <div class="header-actions">
        <el-select
          v-model="query.status"
          placeholder="筛选状态"
          clearable
          @change="fetchData"
          class="status-filter"
        >
          <el-option
            v-for="opt in statusOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <el-table :data="tableData" v-loading="loading" class="data-table">
        <!-- Hazard Title Column -->
        <el-table-column prop="hazard_title" label="关联隐患" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="title-text">{{ row.hazard_title }}</span>
          </template>
        </el-table-column>

        <!-- Assignee Column -->
        <el-table-column prop="assignee_name" label="整改负责人" width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="user-avatar">{{ row.assignee_name?.charAt(0) || '?' }}</span>
              <span>{{ row.assignee_name || '-' }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- Description Column -->
        <el-table-column prop="description" label="整改要求" min-width="160" show-overflow-tooltip />

        <!-- Deadline Column -->
        <el-table-column prop="deadline" label="整改截止时间" width="130">
          <template #default="{ row }">
            <span class="deadline-text">{{ row.deadline || '-' }}</span>
          </template>
        </el-table-column>

        <!-- Status Column -->
        <el-table-column prop="status_name" label="状态" width="110">
          <template #default="{ row }">
            <span class="status-badge" :style="{ '--status-color': getStatusConfig(row.status).color }">
              <span class="status-dot"></span>
              {{ row.status_name }}
            </span>
          </template>
        </el-table-column>

        <!-- Assigner Column -->
        <el-table-column prop="assigner_name" label="派单人" width="100" />

        <!-- Created At Column -->
        <el-table-column prop="created_at" label="派单时间" width="170">
          <template #default="{ row }">
            <span class="time-text">{{ row.created_at || '-' }}</span>
          </template>
        </el-table-column>

        <!-- Actions Column -->
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <button
              v-if="row.status === 'submitted'"
              class="action-btn action-btn--primary"
              @click="handleReview(row)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 11 12 14 22 4"/>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
              验收
            </button>
            <span v-else class="no-action">-</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Pagination -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="query.page"
        :page-size="query.page_size"
        :total="query.total"
        @current-change="fetchData"
        layout="total, prev, pager, next"
        background
      />
    </div>

    <!-- Review Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="整改验收"
      width="480px"
      class="review-dialog"
    >
      <el-form :model="reviewForm" label-position="top" class="review-form">
        <el-form-item label="验收结果" required>
          <div class="radio-group">
            <label class="radio-option" :class="{ active: reviewForm.result === 'passed' }">
              <input type="radio" value="passed" v-model="reviewForm.result" />
              <span class="radio-icon radio-icon--success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </span>
              <span class="radio-label">通过</span>
            </label>
            <label class="radio-option" :class="{ active: reviewForm.result === 'rejected' }">
              <input type="radio" value="rejected" v-model="reviewForm.result" />
              <span class="radio-icon radio-icon--danger">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </span>
              <span class="radio-label">驳回</span>
            </label>
          </div>
        </el-form-item>
        <el-form-item label="验收备注">
          <el-input
            v-model="reviewForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入验收备注（可选）"
            class="form-textarea"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn--ghost" @click="dialogVisible = false">取消</button>
          <button class="btn btn--primary" @click="handleSubmitReview">提交验收</button>
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

.status-filter {
  width: 160px;
}

:deep(.status-filter .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
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

:deep(.el-table__body .cell) {
  white-space: nowrap;
}

/* Title Text */
.title-text {
  font-weight: 500;
  color: #0f172a;
}

/* User Cell */
.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

/* Deadline Text */
.deadline-text {
  font-size: 13px;
  color: #64748b;
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
  background: color-mix(in srgb, var(--status-color) 15%, transparent);
  color: var(--status-color);
  white-space: nowrap;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--status-color);
}

/* Time Text */
.time-text {
  font-size: 13px;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
}

/* Action Button */
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 8px;
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  white-space: nowrap;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.action-btn--primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.action-btn--primary:hover {
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  transform: translateY(-1px);
}

.no-action {
  color: #94a3b8;
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
:deep(.review-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.review-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  margin: 0;
}

:deep(.review-dialog .el-dialog__title) {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-weight: 600;
  color: #0f172a;
}

:deep(.review-dialog .el-dialog__body) {
  padding: 24px;
}

.review-form :deep(.el-form-item__label) {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-weight: 600;
  color: #334155;
  font-size: 13px;
}

/* Radio Group */
.radio-group {
  display: flex;
  gap: 16px;
}

.radio-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.radio-option input {
  display: none;
}

.radio-option:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.radio-option.active {
  border-color: var(--active-color);
  background: color-mix(in srgb, var(--active-color) 5%, transparent);
}

.radio-option:has(input[value="passed"]).active {
  --active-color: #10b981;
}

.radio-option:has(input[value="rejected"]).active {
  --active-color: #ef4444;
}

.radio-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.radio-icon svg {
  width: 20px;
  height: 20px;
}

.radio-icon--success {
  background: #d1fae5;
  color: #10b981;
}

.radio-icon--danger {
  background: #fee2e2;
  color: #ef4444;
}

.radio-label {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.form-textarea {
  width: 100%;
}

:deep(.form-textarea .el-textarea__inner) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
}

:deep(.form-textarea .el-textarea__inner:focus) {
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2), 0 0 0 1px #06b6d4;
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
</style>
