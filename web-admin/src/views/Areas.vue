<script setup>
import { ref, onMounted } from 'vue'
import { getAreas, createArea, updateArea, deleteArea } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const form = ref({})

const areaTypeOptions = [
  { value: 'building', label: '教学楼' },
  { value: 'dormitory', label: '宿舍楼' },
  { value: 'canteen', label: '食堂' },
  { value: 'playground', label: '操场' },
  { value: 'corridor', label: '楼道' },
  { value: 'fire_exit', label: '消防通道' },
  { value: 'other', label: '其他' }
]

onMounted(fetchData)

async function fetchData() {
  loading.value = true
  try {
    const res = await getAreas()
    tableData.value = res.data.results || res.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  form.value = {}
  dialogVisible.value = true
}

function handleEdit(row) {
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    if (form.value.id) {
      await updateArea(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createArea(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除该区域吗？', '提示', { type: 'warning' })
    .then(async () => {
      await deleteArea(row.id)
      ElMessage.success('删除成功')
      fetchData()
    }).catch(() => {})
}
</script>

<template>
  <div class="page-container">
    <div class="toolbar">
      <h2>区域管理</h2>
      <el-button type="primary" @click="handleAdd">新增区域</el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe row-key="id" default-expand-all>
      <el-table-column prop="name" label="区域名称" />
      <el-table-column prop="code" label="区域编码" />
      <el-table-column prop="area_type_name" label="区域类型" />
      <el-table-column prop="point_count" label="点位数量" />
      <el-table-column prop="is_active" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="区域信息" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="区域名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="区域编码">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="区域类型">
          <el-select v-model="form.area_type">
            <el-option v-for="opt in areaTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
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