<script setup>
import { ref, onMounted } from 'vue'
import { getPoints, getAreas, createPoint, updatePoint, deletePoint } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const areas = ref([])
const dialogVisible = ref(false)
const form = ref({})

const frequencyOptions = [
  { value: 'daily', label: '每日' },
  { value: 'weekly', label: '每周' },
  { value: 'monthly', label: '每月' }
]

onMounted(async () => {
  await Promise.all([fetchData(), fetchAreas()])
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getPoints()
    tableData.value = res.data.results || res.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function fetchAreas() {
  try {
    const res = await getAreas({ is_active: 'true' })
    areas.value = res.data.results || res.data
  } catch (error) {
    console.error('Failed to load areas:', error)
  }
}

function handleAdd() {
  form.value = { is_active: true, inspection_frequency: 'daily' }
  dialogVisible.value = true
}

function handleEdit(row) {
  form.value = { ...row, responsible_users: row.responsible_users || [] }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    if (form.value.id) {
      await updatePoint(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createPoint(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除该点位吗？', '提示', { type: 'warning' })
    .then(async () => {
      await deletePoint(row.id)
      ElMessage.success('删除成功')
      fetchData()
    }).catch(() => {})
}
</script>

<template>
  <div class="page-container">
    <div class="toolbar">
      <h2>巡检点位管理</h2>
      <el-button type="primary" @click="handleAdd">新增点位</el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="name" label="点位名称" />
      <el-table-column prop="code" label="点位编码" />
      <el-table-column prop="area_name" label="所属区域" />
      <el-table-column prop="location" label="具体位置" />
      <el-table-column prop="frequency_name" label="巡检频次" />
      <el-table-column prop="responsible_names" label="负责人">
        <template #default="{ row }">
          <el-tag v-for="name in row.responsible_names" :key="name" size="small" style="margin-right: 4px">
            {{ name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="点位信息" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="点位名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="点位编码">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="所属区域">
          <el-select v-model="form.area" placeholder="请选择区域">
            <el-option v-for="area in areas" :key="area.id" :label="area.name" :value="area.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="具体位置">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="巡检频次">
          <el-select v-model="form.inspection_frequency">
            <el-option v-for="opt in frequencyOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="巡检内容">
          <el-input v-model="form.inspection_content" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-container { background: white; border-radius: 8px; padding: 20px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.toolbar h2 { margin: 0; }
</style>