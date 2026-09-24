import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notesApi } from '@/api/notes'
import type { Note, NoteListItem, AesLog, RoundKeys } from '@/api/types'

export const useNotesStore = defineStore('notes', () => {
  const notes = ref<NoteListItem[]>([])
  const currentNote = ref<Note | null>(null)
  const aesLog = ref<AesLog | null>(null)
  const roundKeys = ref<RoundKeys | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      notes.value = await notesApi.list()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Gagal memuat catatan'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: string) {
    loading.value = true
    error.value = null
    try {
      currentNote.value = await notesApi.get(id)
      return currentNote.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Gagal memuat catatan'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function create(title: string, body: string) {
    loading.value = true
    error.value = null
    try {
      const res = await notesApi.create({ title, body })
      await fetchAll()
      return res.id
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Gagal membuat catatan'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function update(id: string, title: string, body: string) {
    loading.value = true
    error.value = null
    try {
      await notesApi.update(id, { title, body })
      await fetchOne(id)
      await fetchAll()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Gagal memperbarui catatan'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function remove(id: string) {
    loading.value = true
    error.value = null
    try {
      await notesApi.remove(id)
      notes.value = notes.value.filter((n) => n.id !== id)
      if (currentNote.value?.id === id) {
        currentNote.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Gagal menghapus catatan'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAesLog(id: string) {
    try {
      aesLog.value = await notesApi.getAesLog(id)
      return aesLog.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Gagal memuat log AES'
      throw err
    }
  }

  async function fetchRoundKeys(id: string) {
    try {
      roundKeys.value = await notesApi.getRoundKeys(id)
      return roundKeys.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Gagal memuat round keys'
      throw err
    }
  }

  function clearCurrentNote() {
    currentNote.value = null
  }

  function clearAesData() {
    aesLog.value = null
    roundKeys.value = null
  }

  return {
    notes,
    currentNote,
    aesLog,
    roundKeys,
    loading,
    error,
    fetchAll,
    fetchOne,
    create,
    update,
    remove,
    fetchAesLog,
    fetchRoundKeys,
    clearCurrentNote,
    clearAesData,
  }
})