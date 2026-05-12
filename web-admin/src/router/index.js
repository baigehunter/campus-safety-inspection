import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue')
      },
      {
        path: 'areas',
        name: 'Areas',
        component: () => import('../views/Areas.vue')
      },
      {
        path: 'points',
        name: 'Points',
        component: () => import('../views/Points.vue')
      },
      {
        path: 'records',
        name: 'Records',
        component: () => import('../views/Records.vue')
      },
      {
        path: 'hazards',
        name: 'Hazards',
        component: () => import('../views/Hazards.vue')
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('../views/Tasks.vue')
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('../views/Logs.vue')
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('../views/Notifications.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (!to.meta.public && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.public && userStore.isLoggedIn && to.path === '/login') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router