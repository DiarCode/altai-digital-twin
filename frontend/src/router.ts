import { createRouter, createWebHistory } from 'vue-router'
import WelcomePage from '@/modules/auth/pages/welcome-page.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: WelcomePage,
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/modules/auth/pages/login-page.vue'),
    },

    {
      path: '/onboarding/personal',
      name: 'onboarding-personal',
      component: () => import('@/modules/onboarding/pages/personal-page.vue'),
    },

    {
      path: '/onboarding/face',
      name: 'onboarding-face',
      component: () => import('@/modules/onboarding/pages/face-page.vue'),
    },

    {
      path: '/onboarding/interview',
      name: 'onboarding-interview',
      component: () => import('@/modules/onboarding/pages/interview-page.vue'),
    },

    {
      path: '/home',
      name: 'home',
      component: () => import('@/modules/home/pages/home-page.vue'),
    },
  ],
})

export default router
