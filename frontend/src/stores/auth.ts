import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const sessionToken = ref<string | null>(null)
  const isLocked = ref(true)
  const pinSetupDone = ref(false)
  const lockoutUntil = ref<number | null>(null)
  const failedAttempts = ref(0)

  const isLockoutActive = computed(() => {
    if (!lockoutUntil.value) return false
    return Date.now() < lockoutUntil.value
  })

  const lockoutSecondsLeft = computed(() => {
    if (!lockoutUntil.value) return 0
    return Math.max(0, Math.ceil((lockoutUntil.value - Date.now()) / 1000))
  })

  async function setupPin(pin: string) {
    const res = await authApi.setup(pin)
    pinSetupDone.value = true
    return res
  }

  async function login(pin: string) {
    if (isLockoutActive.value) {
      throw new Error(`Terlalu banyak percobaan. Coba lagi dalam ${lockoutSecondsLeft.value} detik.`)
    }

    try {
      const res = await authApi.unlock(pin)
      sessionToken.value = res.token
      isLocked.value = false
      failedAttempts.value = 0
      lockoutUntil.value = null
      return res
    } catch (err) {
      failedAttempts.value++
      if (failedAttempts.value >= 5) {
        lockoutUntil.value = Date.now() + 60000
      }
      throw err
    }
  }

  async function lock() {
    if (sessionToken.value) {
      try {
        await authApi.lock()
      } catch {
        // ignore error, lock locally anyway
      }
    }
    sessionToken.value = null
    isLocked.value = true
  }

  function setPinSetupDone(value: boolean) {
    pinSetupDone.value = value
  }

  function restoreSession(token: string) {
    sessionToken.value = token
    isLocked.value = false
  }

  return {
    sessionToken,
    isLocked,
    pinSetupDone,
    lockoutUntil,
    failedAttempts,
    isLockoutActive,
    lockoutSecondsLeft,
    setupPin,
    login,
    lock,
    setPinSetupDone,
    restoreSession,
  }
})