<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { AppButton, AppInput, AppCard } from '@/components'

const router = useRouter()
const authStore = useAuthStore()

const pin = ref('')
const error = ref('')
const loading = ref(false)
const showSetup = computed(() => !authStore.pinSetupDone)

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    if (showSetup.value) {
      await authStore.setupPin(pin.value)
    } else {
      await authStore.login(pin.value)
    }
    router.push('/notes')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Terjadi kesalahan'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const input = document.getElementById('pin-input')
  input?.focus()
})
</script>

<template>
  <div class="lock-view">
    <AppCard class="lock-card" padding="lg">
      <div class="lock-header">
        <h1 class="lock-title">SecretNotes</h1>
        <p v-if="showSetup" class="lock-subtitle">Buat PIN untuk memulai</p>
        <p v-else class="lock-subtitle">Masukkan PIN untuk membuka</p>
      </div>

      <p v-if="error" class="lock-error" role="alert">{{ error }}</p>

      <form @submit.prevent="handleSubmit" class="lock-form">
        <AppInput
          id="pin-input"
          v-model="pin"
          type="password"
          :placeholder="showSetup ? 'PIN minimal 6 karakter' : 'Masukkan PIN'"
          :error="error"
          :disabled="loading"
          autocomplete="one-time-code"
          required
          @keydown.enter.prevent="handleSubmit"
        />

        <div v-if="showSetup" class="lock-hint">
          PIN akan di-hash dengan bcrypt dan tidak pernah disimpan sebagai plaintext.
        </div>

        <AppButton
          type="submit"
          variant="primary"
          size="lg"
          :loading="loading"
          class="lock-submit"
        >
          {{ showSetup ? 'Buat PIN & Masuk' : 'Buka' }}
        </AppButton>
      </form>

      <p v-if="authStore.isLockoutActive" class="lock-lockout">
        Terlalu banyak percobaan gagal. Coba lagi dalam {{ authStore.lockoutSecondsLeft }} detik.
      </p>
    </AppCard>
  </div>
</template>

<style scoped>
.lock-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.lock-card {
  width: 100%;
  max-width: 360px;
}

.lock-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.lock-title {
  font-size: var(--text-section);
  margin-bottom: var(--space-1);
}

.lock-subtitle {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  margin: 0;
}

.lock-error {
  margin: 0 0 var(--space-4);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-small);
  color: var(--color-error);
  background-color: rgba(239, 68, 68, 0.08);
  border-radius: var(--radius-md);
  text-align: center;
}

.lock-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.lock-hint {
  margin: 0;
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  text-align: center;
}

.lock-submit {
  width: 100%;
}

.lock-lockout {
  margin: var(--space-4) 0 0;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-small);
  color: var(--color-warning);
  background-color: rgba(245, 158, 11, 0.08);
  border-radius: var(--radius-md);
  text-align: center;
}
</style>