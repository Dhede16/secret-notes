<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '@/stores/notes'
import { AppButton, AppInput, AppCard } from '@/components'

const route = useRoute()
const router = useRouter()
const notesStore = useNotesStore()

const isEditing = computed(() => !!route.params.id)
const noteId = computed(() => route.params.id as string)

const title = ref('')
const body = ref('')
const saving = ref(false)
const deleting = ref(false)
const titleError = ref('')
const bodyError = ref('')
const saved = ref(false)

async function loadNote() {
  if (isEditing.value) {
    try {
      const note = await notesStore.fetchOne(noteId.value)
      title.value = note.title
      body.value = note.body
    } catch {
      router.push('/notes')
    }
  }
}

async function handleSave() {
  titleError.value = ''
  bodyError.value = ''

  if (!title.value.trim()) {
    titleError.value = 'Judul tidak boleh kosong'
    return
  }
  if (!body.value.trim()) {
    bodyError.value = 'Isi tidak boleh kosong'
    return
  }

  saving.value = true
  saved.value = false
  try {
    if (isEditing.value) {
      await notesStore.update(noteId.value, title.value, body.value)
    } else {
      await notesStore.create(title.value, body.value)
    }
    saved.value = true
    setTimeout(() => {
      router.push('/notes')
    }, 800)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Gagal menyimpan'
    if (message.includes('judul')) titleError.value = message
    else if (message.includes('isi')) bodyError.value = message
    else bodyError.value = message
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!isEditing.value) return

  const confirmed = window.confirm('Hapus catatan ini? Tindakan ini tidak dapat dibatalkan.')
  if (!confirmed) return

  deleting.value = true
  try {
    await notesStore.remove(noteId.value)
    router.push('/notes')
  } catch (err) {
    alert(err instanceof Error ? err.message : 'Gagal menghapus')
  } finally {
    deleting.value = false
  }
}

onMounted(loadNote)

watch(() => route.params.id, loadNote)
</script>

<template>
  <div class="editor-view">
    <header class="editor-header">
      <AppButton variant="ghost" size="sm" @click="$router.push('/notes')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Kembali
      </AppButton>
      <h1 class="editor-title">{{ isEditing ? 'Edit Catatan' : 'Catatan Baru' }}</h1>
      <div class="editor-header__actions">
        <AppButton
          v-if="isEditing"
          variant="ghost"
          size="sm"
          @click="$router.push(`/notes/${noteId}/aes-lab`)"
        >
          AES Lab
        </AppButton>
      </div>
    </header>

    <main class="editor-main">
      <AppCard padding="lg" class="editor-card">
        <form @submit.prevent="handleSave" class="editor-form">
          <AppInput
            v-model="title"
            label="Judul"
            placeholder="Judul catatan"
            :error="titleError"
            :disabled="saving"
            required
            maxlength="200"
          />

          <AppInput
            v-model="body"
            label="Isi"
            placeholder="Tulis catatan Anda di sini..."
            :error="bodyError"
            :disabled="saving"
            required
            textarea
            :rows="12"
          />

          <div class="editor-actions">
            <AppButton
              v-if="isEditing"
              variant="destructive"
              size="md"
              :loading="deleting"
              @click="handleDelete"
            >
              Hapus
            </AppButton>
            <div class="editor-actions__right">
              <span v-if="saved" class="editor-saved">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
                Tersimpan
              </span>
              <AppButton
                type="submit"
                variant="primary"
                size="md"
                :loading="saving"
              >
                {{ isEditing ? 'Simpan Perubahan' : 'Simpan Catatan' }}
              </AppButton>
            </div>
          </div>
        </form>
      </AppCard>
    </main>
  </div>
</template>

<style scoped>
.editor-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--container-padding);
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-surface);
  position: sticky;
  top: 0;
  z-index: 10;
}

.editor-title {
  font-size: var(--text-section);
  margin: 0;
  flex: 1;
  text-align: center;
}

.editor-header__actions {
  display: flex;
  gap: var(--space-2);
  min-width: 48px;
}

.editor-main {
  flex: 1;
  padding: var(--space-6) var(--container-padding);
  max-width: 720px;
  width: 100%;
  margin: 0 auto;
}

.editor-card {
  width: 100%;
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.editor-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-2);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}

.editor-actions__right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.editor-saved {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-small);
  color: var(--color-success);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .editor-header {
    padding: var(--space-3) var(--space-4);
  }
  .editor-title {
    font-size: var(--text-subhead);
  }
  .editor-main {
    padding: var(--space-4);
  }
}
</style>