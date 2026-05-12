// 获取基础URL - H5使用代理，小程序使用完整地址
function getBaseUrl(): string {
  // @ts-ignore
  if (typeof window !== 'undefined') {
    // H5环境 - 使用相对路径，通过vite代理
    return '/api'
  }
  // 小程序环境 - 优先从环境变量读取，兼容真机调试
  const envUrl = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (envUrl) {
    return envUrl
  }
  // 默认开发地址（真机调试需用电脑局域网IP，不能用localhost）
  return 'http://120.48.14.99/api'
}

const BASE_URL = getBaseUrl()

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: any
}

let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

function onTokenRefreshed(newToken: string) {
  pendingRequests.forEach(cb => cb(newToken))
  pendingRequests = []
}

function addPendingRequest(cb: (token: string) => void) {
  pendingRequests.push(cb)
}

async function refreshAccessToken(): Promise<string> {
  const refreshToken = uni.getStorageSync('refresh_token')
  if (!refreshToken) {
    throw new Error('无刷新令牌')
  }
  const res: any = await new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + '/token/refresh/',
      method: 'POST',
      data: { refresh: refreshToken },
      header: { 'Content-Type': 'application/json' },
      success: (r: any) => {
        if (r.statusCode >= 200 && r.statusCode < 300) {
          resolve(r.data)
        } else {
          reject(new Error('刷新令牌失败'))
        }
      },
      fail: reject
    })
  })
  const newAccessToken = res.access
  uni.setStorageSync('access_token', newAccessToken)
  return newAccessToken
}

export function request<T = any>(options: RequestOptions): Promise<T> {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('access_token')
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res: any) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // token 过期——尝试静默刷新。这里有个并发问题：
          // 多个请求同时 401 时，只有第一个去刷新，其余的排队等新 token
          if (!isRefreshing) {
            isRefreshing = true
            refreshAccessToken()
              .then(newToken => {
                onTokenRefreshed(newToken)
                options.header = { ...options.header, Authorization: `Bearer ${newToken}` }
                request(options).then(resolve).catch(reject)
              })
              .catch(() => {
                // 刷新也失败了，只能踢回登录页
                uni.removeStorageSync('access_token')
                uni.removeStorageSync('refresh_token')
                uni.removeStorageSync('userInfo')
                uni.reLaunch({ url: '/pages/login/index' })
                reject(new Error('登录已过期'))
              })
              .finally(() => {
                isRefreshing = false
              })
          } else {
            // 排队等第一个请求刷新完，拿到新 token 再重试
            addPendingRequest((newToken: string) => {
              options.header = { ...options.header, Authorization: `Bearer ${newToken}` }
              request(options).then(resolve).catch(reject)
            })
          }
        } else {
          reject(new Error(res.data?.detail || res.data?.error || '请求失败'))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '网络错误'))
      }
    })
  })
}

// 上传单个图片文件
export function uploadImage(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('access_token')
    uni.uploadFile({
      url: BASE_URL + '/upload/',
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          const data = JSON.parse(res.data)
          // 返回完整URL
          const baseUrl = BASE_URL.replace('/api', '')
          resolve(baseUrl + data.url)
        } else {
          reject(new Error('上传失败'))
        }
      },
      fail: reject
    })
  })
}

// 批量上传图片
export async function uploadImages(filePaths: string[]): Promise<string[]> {
  const urls: string[] = []
  for (const path of filePaths) {
    try {
      const url = await uploadImage(path)
      urls.push(url)
    } catch (e) {
      console.error('上传失败:', path, e)
    }
  }
  return urls
}

export const api = {
  login: (data: { username: string; password: string }) =>
    request({ url: '/login/', method: 'POST', data }),

  logout: (refreshToken: string) =>
    request({ url: '/logout/', method: 'POST', data: { refresh: refreshToken } }),

  getPoints: (params?: any) =>
    request({ url: '/points/', data: params }),

  createRecord: (data: any) =>
    request({ url: '/records/', method: 'POST', data }),

  getRecords: (params?: any) =>
    request({ url: '/records/', data: params }),

  createHazard: (data: any) =>
    request({ url: '/hazards/', method: 'POST', data }),

  getHazards: (params?: any) =>
    request({ url: '/hazards/', data: params }),

  getTasks: (params?: any) =>
    request({ url: '/tasks/', data: params }),

  submitRectify: (id: number, data: any) =>
    request({ url: `/tasks/${id}/submit_rectify/`, method: 'POST', data }),

  // AI 分析走豆包（火山方舟），后面如果换模型改这里就行
  analyzeHazard: (data: { description: string; photos: string[] }) =>
    request({ url: '/analyze/', method: 'POST', data }),

  analyzeInspection: (data: { description: string; photos: string[] }) =>
    request({ url: '/analyze-inspection/', method: 'POST', data }),

  getNotifications: (params?: any) =>
    request({ url: '/notifications/', data: params }),
  markRead: (id: number) =>
    request({ url: `/notifications/${id}/mark_read/`, method: 'POST' }),
  markAllRead: () =>
    request({ url: '/notifications/read_all/', method: 'POST' }),
  getUnreadCount: () =>
    request({ url: '/notifications/unread_count/' }),

  getOpenId: (code: string) =>
    request({ url: '/wx/get_openid/', method: 'POST', data: { code } }),
  getWxTemplates: () =>
    request({ url: '/wx/templates/' }),
  updateSubscribe: (templates: string[]) =>
    request({ url: '/wx/subscribe/', method: 'POST', data: { templates } }),

  getUserInfo: () =>
    request({ url: '/users/' }),
}

export default api
