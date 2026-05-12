<script setup>
import { ref, onMounted } from 'vue'
import { getLogs } from '../api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const query = ref({ page: 1, page_size: 20, total: 0 })

const actionMap = {
  login: '登录',
  logout: '登出',
  create: '创建',
  update: '更新',
  delete: '删除',
  export: '导出'
}

onMounted(fetchData)

async function fetchData() {
  loading.value = true
  try {
    const res = await getLogs(query.value)
    tableData.value = res.data.results || res.data
    query.value.total = res.data.count || tableData.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <div class="toolbar">
      <h2>操作日志</h2>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="user_name" label="操作人" />
      <el-table-column prop="action_name" label="操作类型">
        <template #default="{ row }">
          <el-tag>{{ actionMap[row.action] || row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="model_name" label="操作模型" />
      <el-table-column prop="description" label="操作描述" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP地址" width="130" />
      <el-table-column prop="created_at" label="操作时间" />
    </el-table>

    <el-pagination
      v-model:current-page="query.page"
      :page-size="query.page_size"
      :total="query.total"
      @current-change="fetchData"
      layout="total, prev, pager, next"
      style="margin-top: 20px; justify-content: flex-end"
    />
  </div>
</template>

<style scoped>
.page-container { background: white; border-radius: 8px; padding: 20px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.toolbar h2 { margin: 0; }
</style>