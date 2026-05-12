import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截 —— 自动带 token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截 —— 401 自动刷新 token，并发请求排队等新 token
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        const res = await axios.post('/api/token/refresh/', {
          refresh
        })
        localStorage.setItem('access_token', res.data.access)
        originalRequest.headers.Authorization = `Bearer ${res.data.access}`
        return api(originalRequest)
      } catch (e) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const login = (data) => api.post('/login/', data)
export const logout = (data) => api.post('/logout/', data)

export const getUsers = (params) => api.get('/users/', { params })
export const createUser = (data) => api.post('/users/', data)
export const updateUser = (id, data) => api.put(`/users/${id}/`, data)
export const disableUser = (id) => api.delete(`/users/${id}/`)
export const deleteUser = (id) => api.post(`/users/${id}/delete_user/`)
export const resetPassword = (data) => api.post('/users/reset_password/', data)

export const getAreas = (params) => api.get('/areas/', { params })
export const createArea = (data) => api.post('/areas/', data)
export const updateArea = (id, data) => api.put(`/areas/${id}/`, data)
export const deleteArea = (id) => api.delete(`/areas/${id}/`)

export const getPoints = (params) => api.get('/points/', { params })
export const createPoint = (data) => api.post('/points/', data)
export const updatePoint = (id, data) => api.put(`/points/${id}/`, data)
export const deletePoint = (id) => api.delete(`/points/${id}/`)

export const getRecords = (params) => api.get('/records/', { params })
export const createRecord = (data) => api.post('/records/', data)

export const getHazards = (params) => api.get('/hazards/', { params })
export const createHazard = (data) => api.post('/hazards/', data)
export const updateHazard = (id, data) => api.put(`/hazards/${id}/`, data)
export const assignHazard = (id, data) => api.post(`/hazards/${id}/assign/`, data)

export const getTasks = (params) => api.get('/tasks/', { params })
export const createTask = (data) => api.post('/tasks/', data)
export const submitRectify = (id, data) => api.post(`/tasks/${id}/submit_rectify/`, data)
export const reviewTask = (id, data) => api.post(`/tasks/${id}/review/`, data)

export const getDashboardStats = () => api.get('/dashboard/stats/')
export const getChartData = () => api.get('/dashboard/chart_data/')

export const getNotifications = (params) => api.get('/notifications/', { params })
export const markNotificationRead = (id) => api.post(`/notifications/${id}/mark_read/`)
export const markAllNotificationsRead = () => api.post('/notifications/read_all/')
export const getUnreadCount = () => api.get('/notifications/unread_count/')

export const getLogs = (params) => api.get('/logs/', { params })

export default api
