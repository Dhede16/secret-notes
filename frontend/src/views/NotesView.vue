<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotesStore } from '@/stores/notes'
import { useIdleLock } from '@/composables/useIdleLock'
import { AppButton, AppCard, TimerIndicator, NoteCard } from '@/components'

const router = useRouter()
const authStore = useAuthStore()
const notesStore = useNotesStore()
const { secondsLeft } = useIdleLock()

onMounted(async () => {
  await notesStore.fetchAll()
})

const handleCreate = () => {
  router.push('/notes/new')
}

const handleLock = async () => {
  await authStore.lock()
  router.push('/lock')
}

const handleOpen = (id: string) => {
  router.push(`/notes/${id}`)
}
</script>

<template>
  <div class="notes-view">
    <header class="notes-header">
      <div class="notes-header__left">
        <h1 class="notes-title">Catatan</h1>
      </div>
      <div class="notes-header__right">
        <TimerIndicator :seconds-left="secondsLeft" />
        <AppButton variant="ghost" size="sm" @click="handleLock">
          Kunci
        </AppButton>
      </div>
    </header>

    <main class="notes-main">
      <AppCard v-if="notesStore.notes.length === 0" class="notes-empty" padding="lg">
        <div class="empty-state">
          <p class="empty-state__text">Belum ada catatan</p>
          <AppButton variant="primary" @click="handleCreate">
            Buat Catatan Baru
          </AppButton>
        </div>
      </AppCard>

      <div v-else class="notes-list">
        <NoteCard
          v-for="note in notesStore.notes"
          :key="note.id"
          :note="note"
          @click="handleOpen(note.id)"
        />
      </div>
    </main>

    <AppButton
      v-if="notesStore.notes.length > 0"
      variant="primary"
      size="lg"
      class="notes-fab"
      @click="handleCreate"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <line x1="12" y1="5" x2="12" y2="19" />
        <line x1="5" y1="12" x2="19" y2="12" />
      </svg>
      Catatan Baru
    </AppButton>
  </div>
</template>

<style scoped>
.notes-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.notes-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--container-padding);
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-surface);
  position: sticky;
  top: 0;
  z-index: 10;
}

.notes-title {
  font-size: var(--text-section);
  margin: 0;
}

.notes-header__right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.notes-main {
  flex: 1;
  padding: var(--space-6) var(--container-padding);
  max-width: var(--container-max);
  width: 100%;
}

.notes-empty {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
}

.empty-state {
  text-align: center;
  padding: var(--space-8) var(--space-4);
}

.empty-state__text {
  margin: 0 0 var(--space-4);
  font-size: var(--text-body);
  color: var(--color-text-secondary);
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-width: 640px;
  margin: 0 auto;
  width: 100%;
}

.notes-fab {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  box-shadow: var(--shadow-button-hover);
  z-index: 20;
}

@media (max-width: 640px) {
  .notes-fab {
    left: var(--container-padding);
    right: var(--container-padding);
    bottom: var(--container-padding);
    width: auto;
  }
}
</style>