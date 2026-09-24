import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function fetchWithAuth<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const authStore = useAuthStore()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (authStore.sessionToken) {
    ;(headers as Record<string, string>)['Authorization'] = `Bearer ${authStore.sessionToken}`
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    authStore.lock()
    router.push('/lock')
    throw new Error('Sesi berakhir, silakan login kembali')
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Terjadi kesalahan' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

export const authApi = {
  setup(pin: string) {
    return fetchWithAuth<{ token: string; expires_in: number }>('/auth/setup', {
      method: 'POST',
      body: JSON.stringify({ pin }),
    })
  },

  unlock(pin: string) {
    return fetchWithAuth<{ token: string; expires_in: number }>('/auth/unlock', {
      method: 'POST',
      body: JSON.stringify({ pin }),
    })
  },

  lock() {
    return fetchWithAuth<void>('/auth/lock', {
      method: 'POST',
    })
  },
}

export const notesApi = {
  list() {
    return fetchWithAuth<import('@/api/types').NoteListItem[]>('/notes')
  },

  get(id: string) {
    return fetchWithAuth<import('@/api/types').Note>(`/notes/${id}`)
  },

  create(data: { title: string; body: string }) {
    return fetchWithAuth<{ id: string }>('/notes', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  update(id: string, data: { title: string; body: string }) {
    return fetchWithAuth<void>(`/notes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  remove(id: string) {
    return fetchWithAuth<void>(`/notes/${id}`, {
      method: 'DELETE',
    })
  },

  getAesLog(id: string) {
    return fetchWithAuth<import('@/api/types').AesLog>(`/notes/${id}/aes-log`)
  },

  getRoundKeys(id: string) {
    return fetchWithAuth<import('@/api/types').RoundKeys>(`/notes/${id}/round-keys`)
  },
}