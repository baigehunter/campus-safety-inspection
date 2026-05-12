<script setup>
import { ref, onMounted } from 'vue'
import { getRecords } from '../api'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref([])
const query = ref({ page: 1, page_size: 10, start_date: '', end_date: '', total: 0 })
const expandedRows = ref([])

onMounted(fetchData)

function getImageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (path.startsWith('/media')) return path
  return path
}

function isValidImage(path) {
  return path && !path.startsWith('blob:')
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getRecords(query.value)
    tableData.value = res.data.results || res.data
    query.value.total = res.data.count || tableData.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
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
        <h1 class="page-title">巡检记录</h1>
        <p class="page-subtitle">查看校园安全巡检记录</p>
      </div>
      <div class="header-actions">
        <el-date-picker v-model="query.start_date" type="date" placeholder="开始日期" value-format="YYYY-MM-DD" class="date-picker" />
        <span class="date-sep">至</span>
        <el-date-picker v-model="query.end_date" type="date" placeholder="结束日期" value-format="YYYY-MM-DD" class="date-picker" />
        <el-button type="primary" class="query-btn" @click="fetchData">查询</el-button>
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
              <!-- AI Analysis Result -->
              <div class="expand-section ai-section" v-if="row.ai_analysis || (row.ai_tags && row.ai_tags.length)">
                <h4 class="expand-title">
                  <span class="ai-icon">🤖</span>
                  AI 智能分析结果
                </h4>
                <div class="ai-result-card">
                  <div class="ai-result-row" v-if="row.ai_status">
                    <div class="ai-result-item">
                      <span class="ai-label">AI判断状态</span>
                      <span class="ai-value" :class="row.ai_status === 'abnormal' ? 'text-danger' : 'text-success'">
                        {{ row.ai_status === 'abnormal' ? '异常' : '正常' }}
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

              <!-- Remark -->
              <div class="expand-section">
                <h4 class="expand-title">巡检备注</h4>
                <p class="expand-text">{{ row.remark || '暂无备注' }}</p>
              </div>

              <!-- Photos -->
              <div class="expand-section">
                <h4 class="expand-title">现场照片</h4>
                <div class="photo-grid" v-if="row.inspection_photos && row.inspection_photos.length > 0">
                  <template v-for="(photo, idx) in row.inspection_photos" :key="idx">
                    <el-image
                      v-if="isValidImage(photo)"
                      :src="getImageUrl(photo)"
                      class="photo-item"
                      fit="cover"
                      :preview-src-list="row.inspection_photos.filter(p => isValidImage(p)).map(p => getImageUrl(p))"
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

        <!-- Point Name -->
        <el-table-column prop="point_name" label="巡检点位" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="point-name">{{ row.point_name }}</span>
          </template>
        </el-table-column>

        <!-- Inspector -->
        <el-table-column prop="inspector_name" label="巡检人" min-width="80" />

        <!-- Status -->
        <el-table-column prop="status_name" label="巡检状态" min-width="90">
          <template #default="{ row }">
            <span class="status-badge" :class="row.status === 'normal' ? 'status--normal' : 'status--abnormal'">
              {{ row.status_name }}
            </span>
          </template>
        </el-table-column>

        <!-- AI Status -->
        <el-table-column label="AI判断" min-width="80">
          <template #default="{ row }">
            <span v-if="row.ai_status" class="ai-status-badge" :class="row.ai_status === 'abnormal' ? 'ai--abnormal' : 'ai--normal'">
              {{ row.ai_status === 'abnormal' ? '异常' : '正常' }}
            </span>
            <span v-else class="no-ai">-</span>
          </template>
        </el-table-column>

        <!-- Remark -->
        <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />

        <!-- Inspection Time -->
        <el-table-column prop="inspection_time" label="巡检时间" min-width="150">
          <template #default="{ row }">
            <span class="time-text">{{ formatDateTime(row.inspection_time) }}</span>
          </template>
        </el-table-column>

        <!-- Photos Thumb -->
        <el-table-column label="照片" width="100">
          <template #default="{ row }">
            <el-image
              v-if="row.inspection_photos?.length"
              :src="getImageUrl(row.inspection_photos[0])"
              class="photo-thumb"
              fit="cover"
              :preview-src-list="row.inspection_photos.filter(p => isValidImage(p)).map(p => getImageUrl(p))"
            >
              <template #error>
                <div class="photo-thumb-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <span v-else class="no-photo">-</span>
          </template>
        </el-table-column>

        <!-- Actions -->
        <el-table-column label="操作" min-width="90">
          <template #default="{ row }">
            <div class="action-buttons">
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
  flex-wrap: wrap;
  gap: 16px;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-picker {
  width: 150px;
}

:deep(.date-picker .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
}

.date-sep {
  color: #94a3b8;
  font-size: 14px;
}

.query-btn {
  border-radius: 10px;
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

:deep(.el-table__expand-icon) {
  color: #94a3b8;
}

:deep(.el-table__expand-icon:hover) {
  color: #06b6d4;
}

/* Point Name */
.point-name {
  font-weight: 500;
  color: #0f172a;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status--normal {
  background: #d1fae5;
  color: #059669;
}

.status--abnormal {
  background: #fee2e2;
  color: #dc2626;
}

/* AI Status Badge */
.ai-status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.ai--normal {
  background: #dbeafe;
  color: #1d4ed8;
}

.ai--abnormal {
  background: #fee2e2;
  color: #dc2626;
}

.no-ai {
  color: #94a3b8;
  font-size: 13px;
}

/* Time */
.time-text {
  font-size: 13px;
  color: #64748b;
}

/* Photo Thumb */
.photo-thumb {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
}

.photo-thumb-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: #f1f5f9;
  border-radius: 8px;
  color: #94a3b8;
}

.no-photo {
  color: #94a3b8;
  font-size: 13px;
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

/* AI Section */
.ai-section {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 12px;
  padding: 20px;
  margin: -8px -8px 8px -8px;
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

.ai-value.text-danger { color: #dc2626; }
.ai-value.text-success { color: #059669; }

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
</style>
