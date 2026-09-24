import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const DEFAULT_TIMEOUT = 3 * 60 * 1000 // 3 minutes

export function useIdleLock(timeoutMs = DEFAULT_TIMEOUT) {
  const authStore = useAuthStore()
  const lastActivity = ref(Date.now())
  const tick = ref(0)
  const timerId = ref<ReturnType<typeof setInterval> | null>(null)
  const timeoutId = ref<ReturnType<typeof setTimeout> | null>(null)

  const secondsLeft = computed(() => {
    const elapsed = Date.now() - lastActivity.value
    const remaining = timeoutMs - elapsed
    return Math.max(0, Math.ceil(remaining / 1000))
  })

  function resetTimer() {
    lastActivity.value = Date.now()
  }

  function startIdleTimer() {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
    }
    timeoutId.value = setTimeout(() => {
      handleIdleTimeout()
    }, timeoutMs)

    if (!timerId.value) {
      timerId.value = setInterval(() => {
        tick.value++
      }, 1000)
    }
  }

  function stopIdleTimer() {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
      timeoutId.value = null
    }
    if (timerId.value) {
      clearInterval(timerId.value)
      timerId.value = null
    }
  }

  async function handleIdleTimeout() {
    stopIdleTimer()
    await authStore.lock()
    router.push('/lock')
  }

  function onActivity() {
    if (!authStore.isLocked) {
      resetTimer()
      startIdleTimer()
    }
  }

  onMounted(() => {
    const events = ['mousemove', 'keydown', 'touchstart', 'scroll', 'click']
    events.forEach((event) => {
      window.addEventListener(event, onActivity, { passive: true })
    })

    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && !authStore.isLocked) {
        // Tab became visible, check if we should lock
        const elapsed = Date.now() - lastActivity.value
        if (elapsed >= timeoutMs) {
          handleIdleTimeout()
        } else {
          resetTimer()
          startIdleTimer()
        }
      }
    })

    if (!authStore.isLocked) {
      startIdleTimer()
    }
  })

  onUnmounted(() => {
    const events = ['mousemove', 'keydown', 'touchstart', 'scroll', 'click']
    events.forEach((event) => {
      window.removeEventListener(event, onActivity)
    })
    stopIdleTimer()
  })

  return {
    secondsLeft,
    resetTimer,
    startIdleTimer,
    stopIdleTimer,
  }
}