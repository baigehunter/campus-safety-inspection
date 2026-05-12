import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)

  async function login(username, password) {
    const res = await loginApi({ username, password })
    const { access, refresh, user: userData } = res.data

    accessToken.value = access
    refreshToken.value = refresh
    user.value = userData

    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('user', JSON.stringify(userData))

    return userData
  }

  async function logout() {
    try {
      // 调后端登出接口把 refresh token 拉黑，防止被盗用。
      // 即使后端挂了也不影响前端登出——catch 里直接清本地状态
      const token = localStorage.getItem('refresh_token')
      if (token) {
        await logoutApi({ refresh: token })
      }
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      // 清除本地状态
      user.value = null
      accessToken.value = ''
      refreshToken.value = ''
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  return {
    user,
    accessToken,
    isLoggedIn,
    login,
    logout
  }
})