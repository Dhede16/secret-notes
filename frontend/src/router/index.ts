import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/lock',
      name: 'lock',
      component: () => import('../views/LockView.vue'),
    },
    {
      path: '/notes',
      name: 'notes',
      component: () => import('../views/NotesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/notes/new',
      name: 'note-new',
      component: () => import('../views/NoteEditorView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/notes/:id',
      name: 'note-detail',
      component: () => import('../views/NoteEditorView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/notes/:id/aes-lab',
      name: 'aes-lab',
      component: () => import('../views/AesLabView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/notes',
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.sessionToken) {
    next('/lock')
  } else {
    next()
  }
})

export default router