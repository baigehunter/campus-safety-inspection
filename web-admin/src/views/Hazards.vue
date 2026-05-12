<script setup>
import { ref, onMounted } from 'vue'
import { getHazards, getUsers, assignHazard } from '../api'
import { ElMessage } from 'element-plus'
import { Picture, View, Edit } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref([])
const query = ref({ page: 1, page_size: 10, status: '', total: 0 })
const dialogVisible = ref(false)
const assignForm = ref({})
const expandedRows = ref([])

const statusOptions = [
  { value: 'pending', label: '待处理', color: 'gray' },
  { value: 'assigned', label: '已派单', color: 'blue' },
  { value: 'rectifying', label: '整改中', color: 'orange' },
  { value: 'completed', label: '已完成', color: 'green' },
  { value: 'rejected', label: '已驳回', color: 'red' }
]

const users = ref([])

onMounted(async () => {
  await Promise.all([fetchData(), fetchUsers()])
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getHazards(query.value)
    tableData.value = res.data.results || res.data
    query.value.total = res.data.count || tableData.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function fetchUsers() {
  try {
    const res = await getUsers({ role: 'rectifier' })
    users.value = res.data.results || res.data
  } catch (error) {
    console.error('Failed to load users:', error)
  }
}

function handleAssign(row) {
  assignForm.value = { hazard_id: row.id, assignee_id: '', description: '', deadline: '' }
  dialogVisible.value = true
}

async function handleSubmitAssign() {
  if (!assignForm.value.assignee_id) {
    ElMessage.warning('请选择整改负责人')
    return
  }
  if (!assignForm.value.deadline) {
    ElMessage.warning('请设置整改截止时间')
    return
  }
  try {
    await assignHazard(assignForm.value.hazard_id, {
      assignee_id: assignForm.value.assignee_id,
      description: assignForm.value.description,
      deadline: assignForm.value.deadline
    })
    ElMessage.success('派单成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('派单失败')
  }
}

function toggleExpand(row) {
  const index = expandedRows.value.indexOf(row.id)
  if (index > -1) {
    expandedRows.value.splice(index, 1)
  } else {
    expandedRows.value.push(row.id)
  }
}

function isExpanded(row) {
  return expandedRows.value.includes(row.id)
}

function getImageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (path.startsWith('/media')) return path
  if (path.startsWith('blob:')) return ''
  return path
}

function isValidImage(path) {
  return path && !path.startsWith('blob:')
}

function getStatusConfig(status) {
  const configs = {
    pending: { label: '待处理', class: 'status--pending', icon: '⏳' },
    assigned: { label: '已派单', class: 'status--assigned', icon: '📋' },
    rectifying: { label: '整改中', class: 'status--rectifying', icon: '🔧' },
    completed: { label: '已完成', class: 'status--completed', icon: '✅' },
    rejected: { label: '已驳回', class: 'status--rejected', icon: '❌' }
  }
  return configs[status] || configs.pending
}

function getLevelConfig(level) {
  const configs = {
    general: { label: '一般隐患', class: 'level--general' },
    serious: { label: '重大隐患', class: 'level--serious' }
  }
  return configs[level] || configs.general
}

function getHazardTypeName(type) {
  const names = {
    fire: '消防安全',
    electric: '用电安全',
    building: '建筑安全',
    equipment: '设备安全',
    food: '食品安全',
    other: '其他'
  }
  return names[type] || type
}
</script>

<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">隐患管理</h1>
        <p class="page-subtitle">查看和处理校园安全隐患</p>
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
      <el-table
        :data="tableData"
        v-loading="loading"
        row-key="id"
        :expand-row-keys="expandedRows"
        class="data-table"
      >
        <!-- Expand Column -->
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <!-- AI 分析结果 -->
              <div class="expand-section ai-section" v-if="row.ai_analysis || (row.ai_tags && row.ai_tags.length)">
                <h4 class="expand-title">
                  <span class="ai-icon">🤖</span>
                  AI 智能分析结果
                </h4>
                <div class="ai-result-card">
                  <div class="ai-result-row" v-if="row.ai_hazard_type || row.ai_level">
                    <div class="ai-result-item" v-if="row.ai_hazard_type">
                      <span class="ai-label">AI识别类型</span>
                      <span class="ai-value">{{ getHazardTypeName(row.ai_hazard_type) }}</span>
                    </div>
                    <div class="ai-result-item" v-if="row.ai_level">
                      <span class="ai-label">AI判断等级</span>
                      <span class="ai-value" :class="row.ai_level === 'serious' ? 'text-danger' : 'text-warning'">
                        {{ row.ai_level === 'serious' ? '重大隐患' : '一般隐患' }}
                      </span>
                    </div>
                  </div>
                  <div class="ai-tags-row" v-if="row.ai_tags && row.ai_tags.length">
                    <span class="ai-label">AI标签</span>
                    <div class="ai-tags">
                      <span class="ai-tag" v-for="tag in row.ai_tags" :key="tag">{{ tag }}</span>
                    </div>
                  </div>
                  <div class="ai-analysis-row" v-if="row.ai_analysis">
                    <span class="ai-label">分析结论</span>
                    <p class="ai-analysis-text">{{ row.ai_analysis }}</p>
                  </div>
                </div>
              </div>

              <div class="expand-section">
                <h4 class="expand-title">隐患描述</h4>
                <p class="expand-text">{{ row.description || '暂无描述' }}</p>
              </div>
              <div class="expand-section">
                <h4 class="expand-title">隐患照片</h4>
                <div class="photo-grid" v-if="row.photos && row.photos.length > 0">
                  <template v-for="(photo, idx) in row.photos" :key="idx">
                    <el-image
                      v-if="isValidImage(photo)"
                      :src="getImageUrl(photo)"
                      class="photo-item"
                      fit="cover"
                      :preview-src-list="row.photos.filter(p => isValidImage(p)).map(p => getImageUrl(p))"
                    >
                      <template #error>
                        <div class="photo-error">
                          <el-icon><Picture /></el-icon>
                          <span>加载失败</span>
                        </div>
                      </template>
                    </el-image>
                    <div v-else class="photo-error">
                      <el-icon><Picture /></el-icon>
                      <span>无效图片</span>
                    </div>
                  </template>
                </div>
                <p v-else class="no-data">暂无照片</p>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Title Column -->
        <el-table-column prop="title" label="隐患标题" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="title-text">{{ row.title }}</span>
          </template>
        </el-table-column>

        <!-- Type Column -->
        <el-table-column prop="hazard_type_name" label="隐患类型" min-width="90">
          <template #default="{ row }">
            <span class="type-tag">{{ row.hazard_type_name }}</span>
          </template>
        </el-table-column>

        <!-- Level Column -->
        <el-table-column prop="level_name" label="隐患等级" min-width="90">
          <template #default="{ row }">
            <span class="level-badge" :class="getLevelConfig(row.level).class">
              {{ row.level_name }}
            </span>
          </template>
        </el-table-column>

        <!-- Area Column -->
        <el-table-column prop="area_name" label="所在区域" min-width="100" show-overflow-tooltip />

        <!-- Location Column -->
        <el-table-column prop="location" label="具体位置" min-width="140" show-overflow-tooltip />

        <!-- Reporter Column -->
        <el-table-column prop="reporter_name" label="上报人" min-width="80" />

        <!-- Status Column -->
        <el-table-column prop="status_name" label="状态" min-width="100">
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusConfig(row.status).class">
              {{ getStatusConfig(row.status).icon }} {{ row.status_name }}
            </span>
          </template>
        </el-table-column>

        <!-- Deadline Column -->
        <el-table-column prop="deadline" label="整改期限" min-width="100">
          <template #default="{ row }">
            <span class="deadline-text" :class="{ 'deadline--overdue': false }">
              {{ row.deadline || '-' }}
            </span>
          </template>
        </el-table-column>

        <!-- Actions Column -->
        <el-table-column label="操作" min-width="130">
          <template #default="{ row }">
            <div class="action-buttons">
              <button
                v-if="row.status === 'pending'"
                class="action-btn action-btn--primary"
                @click="handleAssign(row)"
              >
                派单
              </button>
              <button
                class="action-btn action-btn--ghost"
                @click="toggleExpand(row)"
              >
                {{ isExpanded(row) ? '收起' : '详情' }}
              </button>
            </div>
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

    <!-- Assign Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="指派整改任务"
      width="500px"
      class="assign-dialog"
    >
      <el-form :model="assignForm" label-width="100px" class="assign-form">
        <el-form-item label="整改负责人" required>
          <el-select
            v-model="assignForm.assignee_id"
            placeholder="请选择整改负责人"
            class="form-select"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="整改要求">
          <el-input
            v-model="assignForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入整改要求"
            class="form-textarea"
          />
        </el-form-item>
        <el-form-item label="截止时间" required>
          <el-date-picker
            v-model="assignForm.deadline"
            type="datetime"
            placeholder="选择整改截止时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            class="form-datepicker"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn--ghost" @click="dialogVisible = false">取消</button>
          <button class="btn btn--primary" @click="handleSubmitAssign">确定派单</button>
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
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.status-filter {
  width: 160px;
}

:deep(.status-filter .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
}

:deep(.status-filter .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1;
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

/* 单元格内容样式 */
:deep(.el-table__body .cell) {
  display: flex;
  align-items: center;
}

:deep(.el-table__header .cell) {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-table__expand-icon) {
  color: #94a3b8;
}

:deep(.el-table__expand-icon:hover) {
  color: #06b6d4;
}

/* Title Cell */
.title-text {
  font-weight: 500;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

/* Type Tag */
.type-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
  font-weight: 500;
  white-space: nowrap;
}

/* Level Badge */
.level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.level-badge.level--general {
  background: #fef3c7;
  color: #b45309;
}

.level-badge.level--serious {
  background: #fee2e2;
  color: #dc2626;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.status--pending {
  background: #f1f5f9;
  color: #475569;
}

.status-badge.status--assigned {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-badge.status--rectifying {
  background: #fef3c7;
  color: #b45309;
}

.status-badge.status--completed {
  background: #d1fae5;
  color: #059669;
}

.status-badge.status--rejected {
  background: #fee2e2;
  color: #dc2626;
}

/* Deadline Text */
.deadline-text {
  font-size: 13px;
  color: #64748b;
}

.deadline-text.deadline--overdue {
  color: #dc2626;
  font-weight: 500;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 12px;
  border-radius: 6px;
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  white-space: nowrap;
}

.action-btn--primary {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: white;
}

.action-btn--primary:hover {
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
  transform: translateY(-1px);
}

.action-btn--ghost {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.action-btn--ghost:hover {
  background: #f8fafc;
  color: #334155;
  border-color: #cbd5e1;
}

/* ========================================
   Expand Content
   ======================================== */
.expand-content {
  padding: 24px 48px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.expand-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* AI Section Styles */
.ai-section {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 12px;
  padding: 20px;
  margin: -8px -8px 16px -8px;
}

.ai-icon {
  margin-right: 8px;
}

.ai-result-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-result-row {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.ai-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  min-width: 80px;
}

.ai-value {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.ai-value.text-danger {
  color: #dc2626;
}

.ai-value.text-warning {
  color: #b45309;
}

.ai-tags-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.ai-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ai-tag {
  display: inline-block;
  padding: 4px 12px;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.ai-analysis-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-analysis-text {
  color: #334155;
  line-height: 1.7;
  margin: 0;
  font-size: 14px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.expand-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin: 0;
}

.expand-text {
  color: #475569;
  line-height: 1.6;
  margin: 0;
}

.photo-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.photo-item {
  width: 120px;
  height: 120px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.photo-item:hover {
  transform: scale(1.05);
}

.photo-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  background: #f1f5f9;
  border-radius: 12px;
  color: #94a3b8;
  font-size: 12px;
  gap: 8px;
}

.photo-error .el-icon {
  font-size: 24px;
}

.no-data {
  color: #94a3b8;
  font-size: 14px;
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

:deep(.el-pagination.is-background .el-pager li:not(.disabled):hover) {
  color: #06b6d4;
}

/* ========================================
   Dialog Styles
   ======================================== */
:deep(.assign-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.assign-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  margin: 0;
}

:deep(.assign-dialog .el-dialog__title) {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-weight: 600;
  color: #0f172a;
}

:deep(.assign-dialog .el-dialog__body) {
  padding: 24px;
}

.assign-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #334155;
}

.form-select,
.form-textarea,
.form-datepicker {
  width: 100%;
}

:deep(.form-select .el-input__wrapper),
:deep(.form-textarea .el-textarea__inner),
:deep(.form-datepicker .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
}

:deep(.form-select .el-input__wrapper:focus-within),
:deep(.form-textarea .el-textarea__inner:focus),
:deep(.form-datepicker .el-input__wrapper:focus-within) {
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
