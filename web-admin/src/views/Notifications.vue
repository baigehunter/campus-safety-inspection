<script setup>
import { ref, onMounted } from 'vue'
import { getNotifications, markNotificationRead, markAllNotificationsRead, getUnreadCount } from '../api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const query = ref({ page: 1, page_size: 10, total: 0 })
const unreadCount = ref(0)

const categoryOptions = [
  { value: '', label: '全部类别' },
  { value: 'hazard_new', label: '新隐患上报' },
  { value: 'hazard_assigned', label: '隐患已派单' },
  { value: 'rectify_submitted', label: '整改已提交' },
  { value: 'rectify_approved', label: '整改已通过' },
  { value: 'rectify_rejected', label: '整改已驳回' },
  { value: 'inspection_overdue', label: '巡检逾期' },
  { value: 'ai_abnormal', label: 'AI异常检测' },
  { value: 'deadline_approaching', label: '截止临近' },
  { value: 'deadline_overdue', label: '整改逾期' }
]

onMounted(async () => {
  await Promise.all([fetchData(), fetchUnread()])
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getNotifications(query.value)
    tableData.value = res.data.results || res.data
    query.value.total = res.data.count || tableData.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function fetchUnread() {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data.total_unread || 0
  } catch (error) {
    console.error('Failed to load unread count:', error)
  }
}

async function handleMarkRead(row) {
  if (row.is_read) return
  try {
    await markNotificationRead(row.id)
    row.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleMarkAllRead() {
  try {
    await markAllNotificationsRead()
    tableData.value.forEach(r => { r.is_read = true })
    unreadCount.value = 0
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

function getCategoryClass(category) {
  const classes = {
    hazard_new: 'cat--red', hazard_assigned: 'cat--blue',
    rectify_submitted: 'cat--blue', rectify_approved: 'cat--green',
    rectify_rejected: 'cat--red', inspection_overdue: 'cat--orange',
    ai_abnormal: 'cat--purple', deadline_approaching: 'cat--orange',
    deadline_overdue: 'cat--red'
  }
  return classes[category] || 'cat--gray'
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">消息推送</h1>
        <p class="page-subtitle">查看系统推送通知</p>
      </div>
      <div class="header-actions">
        <span class="unread-badge" v-if="unreadCount > 0">{{ unreadCount }} 条未读</span>
        <button class="btn-mark-all" v-if="unreadCount > 0" @click="handleMarkAllRead">全部已读</button>
        <el-select
          v-model="query.category"
          placeholder="筛选类别"
          clearable
          @change="fetchData"
          class="category-filter"
        >
          <el-option v-for="opt in categoryOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <el-table :data="tableData" v-loading="loading" row-key="id" class="data-table">
        <!-- Recipient -->
        <el-table-column prop="recipient_name" label="接收人" min-width="100" />

        <!-- Category -->
        <el-table-column prop="category_name" label="通知类别" min-width="110">
          <template #default="{ row }">
            <span class="category-tag" :class="getCategoryClass(row.category)">{{ row.category_name }}</span>
          </template>
        </el-table-column>

        <!-- Title -->
        <el-table-column prop="title" label="通知标题" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="{ 'unread-text': !row.is_read }">{{ row.title }}</span>
          </template>
        </el-table-column>

        <!-- Body -->
        <el-table-column prop="body" label="通知内容" min-width="250" show-overflow-tooltip />

        <!-- Read Status -->
        <el-table-column label="状态" min-width="80">
          <template #default="{ row }">
            <span class="read-tag" :class="row.is_read ? 'read--yes' : 'read--no'">
              {{ row.is_read ? '已读' : '未读' }}
            </span>
          </template>
        </el-table-column>

        <!-- Created -->
        <el-table-column label="时间" min-width="140">
          <template #default="{ row }">
            <span class="time-text">{{ formatDateTime(row.created_at) }}</span>
          </template>
        </el-table-column>

        <!-- Actions -->
        <el-table-column label="操作" min-width="90">
          <template #default="{ row }">
            <button
              v-if="!row.is_read"
              class="action-btn action-btn--ghost"
              @click="handleMarkRead(row)"
            >
              标记已读
            </button>
            <span v-else class="read-hint">-</span>
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
  </div>
</template>

<style scoped>
.page-container { min-height: 100%; }

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-content { display: flex; flex-direction: column; gap: 4px; }

.page-title {
  font-family: 'Plus Jakarta Sans', 'PingFang SC', sans-serif;
  font-size: 24px; font-weight: 700; color: #0f172a;
  letter-spacing: -0.5px; margin: 0;
}

.page-subtitle { font-size: 14px; color: #64748b; margin: 0; }

.header-actions { display: flex; align-items: center; gap: 10px; }

.unread-badge {
  font-size: 13px; color: #ef4444; font-weight: 500;
}

.btn-mark-all {
  padding: 6px 14px; border-radius: 8px; font-size: 13px; border: 1px solid #e2e8f0;
  background: transparent; color: #64748b; cursor: pointer; transition: all 0.2s;
}
.btn-mark-all:hover { background: #f8fafc; color: #334155; }

.category-filter { width: 150px; }
:deep(.category-filter .el-input__wrapper) { border-radius: 10px; box-shadow: 0 0 0 1px #e2e8f0; }

/* Table */
.table-wrapper {
  background: #ffffff; border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; overflow: hidden;
}
.data-table {
  --el-table-border-color: #f1f5f9; --el-table-header-bg-color: #f8fafc;
  --el-table-header-text-color: #334155; --el-table-row-hover-bg-color: #f8fafc;
}
:deep(.el-table__header th) {
  font-weight: 600; font-size: 13px; text-transform: uppercase;
  letter-spacing: 0.3px; padding: 16px 12px;
}
:deep(.el-table__body td) { padding: 14px 12px; }

.unread-text { font-weight: 600; color: #0f172a; }

/* Category Tag */
.category-tag {
  display: inline-flex; padding: 4px 10px; border-radius: 6px;
  font-size: 12px; font-weight: 500; white-space: nowrap;
}
.cat--red { background: #fef2f2; color: #dc2626; }
.cat--blue { background: #eff6ff; color: #2563eb; }
.cat--green { background: #f0fdf4; color: #059669; }
.cat--orange { background: #fffbeb; color: #d97706; }
.cat--purple { background: #f5f3ff; color: #7c3aed; }
.cat--gray { background: #f8fafc; color: #64748b; }

/* Read Status */
.read-tag { display: inline-flex; padding: 3px 10px; border-radius: 10px; font-size: 12px; font-weight: 500; }
.read--no { background: #fef3c7; color: #b45309; }
.read--yes { background: #f1f5f9; color: #94a3b8; }

.time-text { font-size: 13px; color: #64748b; }

/* Actions */
.action-btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all 0.2s; border: none; white-space: nowrap;
}
.action-btn--ghost { background: transparent; color: #64748b; border: 1px solid #e2e8f0; }
.action-btn--ghost:hover { background: #f8fafc; color: #334155; border-color: #cbd5e1; }
.read-hint { color: #94a3b8; font-size: 13px; }

/* Pagination */
.pagination-wrapper { display: flex; justify-content: flex-end; padding: 20px 0; }
:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) { background: #0f172a; }
</style>
