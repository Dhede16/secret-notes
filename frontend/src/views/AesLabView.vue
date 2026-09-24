<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '@/stores/notes'
import { AppButton, AppCard, HexMatrix, NoteCard } from '@/components'

const route = useRoute()
const router = useRouter()
const notesStore = useNotesStore()

const noteId = computed(() => route.params.id as string)
const activeTab = ref<'block' | 'keys'>('block')
const loading = ref(false)
const error = ref('')

const aesLog = computed(() => notesStore.aesLog)
const roundKeys = computed(() => notesStore.roundKeys)
const currentNote = computed(() => notesStore.currentNote)

const ciphertextMatrix = computed(() => {
  if (!aesLog.value || aesLog.value.rounds.length === 0) return [] as number[][]
  return aesLog.value.rounds[aesLog.value.rounds.length - 1]!.after_add_round_key
})

const originalKeyMatrix = computed(() => {
  if (!roundKeys.value || roundKeys.value.round_keys.length === 0) return [] as number[][]
  const first = roundKeys.value.round_keys[0]
  return first ? first : []
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    if (!currentNote.value || currentNote.value.id !== noteId.value) {
      await notesStore.fetchOne(noteId.value)
    }
    await Promise.all([
      notesStore.fetchAesLog(noteId.value),
      notesStore.fetchRoundKeys(noteId.value),
    ])
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Gagal memuat data AES'
  } finally {
    loading.value = false
  }
}

function getRoundHighlights(roundNum: number) {
  if (!aesLog.value) return []
  const roundData = aesLog.value.rounds.find(r => r.round === roundNum)
  if (!roundData || !roundData.round_key_matrix) return []

  const highlights: Array<{row: number, col: number, type: 'rotword' | 'subword' | 'rcon'}> = []
  const rkMatrix = roundData.round_key_matrix
  rkMatrix.forEach((row, r) => {
    row.forEach((_, c) => {
      highlights.push({ row: r, col: c, type: 'rcon' })
    })
  })
  return highlights
}

function getKeyExpansionHighlights(): Array<{wordIndex: number, type: 'rotword' | 'subword' | 'rcon'}> {
  if (!roundKeys.value) return []

  return roundKeys.value.key_expansion_trace
    .filter(t => t.is_rotword || t.is_subword || t.is_rcon)
    .map(t => ({
      wordIndex: t.word_index,
      type: t.is_rotword ? 'rotword' : t.is_subword ? 'subword' : 'rcon',
    }))
}

onMounted(loadData)
watch(() => route.params.id, loadData)
</script>

<template>
  <div class="aes-lab-view">
    <header class="aes-lab-header">
      <AppButton variant="ghost" size="sm" @click="$router.push(`/notes/${noteId}`)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Kembali
      </AppButton>
      <h1 class="aes-lab-title">AES Lab</h1>
      <div />
    </header>

    <main class="aes-lab-main">
      <AppCard padding="md" class="aes-lab-tabs-card">
        <div class="aes-lab-tabs" role="tablist">
          <button
            role="tab"
            :aria-selected="activeTab === 'block'"
            :class="['aes-lab-tab', { 'aes-lab-tab--active': activeTab === 'block' }]"
            @click="activeTab = 'block'"
          >
            Blok Pertama
          </button>
          <button
            role="tab"
            :aria-selected="activeTab === 'keys'"
            :class="['aes-lab-tab', { 'aes-lab-tab--active': activeTab === 'keys' }]"
            @click="activeTab = 'keys'"
          >
            Round Keys
          </button>
        </div>
      </AppCard>

      <div v-if="loading" class="aes-lab-loading">
        <div class="spinner" aria-hidden="true"></div>
        <p>Memuat visualisasi AES...</p>
      </div>

      <p v-else-if="error" class="aes-lab-error" role="alert">{{ error }}</p>

      <div v-else class="aes-lab-content">
        <!-- Tab: Blok Pertama -->
        <div v-if="activeTab === 'block' && aesLog" class="aes-lab-panel">
          <AppCard padding="md" class="aes-lab-matrix-card">
            <div class="matrix-header">
              <h3>Input Block (Plaintext)</h3>
              <span class="matrix-badge">16 byte pertama</span>
            </div>
            <HexMatrix
              :matrix="aesLog.input_matrix"
              title="Plaintext (Column-Major)"
            />
          </AppCard>

          <AppCard padding="md" class="aes-lab-matrix-card" v-for="round in aesLog.rounds" :key="round.round">
            <div class="matrix-header">
              <h3>Ronde {{ round.round === 0 ? 'Awal (AddRoundKey)' : round.round }}</h3>
            </div>
            
            <div class="round-stages">
              <HexMatrix
                :matrix="round.after_add_round_key"
                title="Setelah AddRoundKey"
                :highlights="round.round > 0 ? getRoundHighlights(round.round) : []"
              />
              
              <div v-if="round.after_sub_bytes" class="round-stages__row">
                <HexMatrix
                  :matrix="round.after_sub_bytes"
                  title="Setelah SubBytes"
                />
                <HexMatrix
                  v-if="round.after_shift_rows"
                  :matrix="round.after_shift_rows"
                  title="Setelah ShiftRows"
                />
              </div>
              
              <HexMatrix
                v-if="round.after_mix_columns"
                :matrix="round.after_mix_columns"
                title="Setelah MixColumns"
              />
            </div>
          </AppCard>

          <AppCard padding="md" class="aes-lab-matrix-card" v-if="aesLog.rounds.length > 0">
            <div class="matrix-header">
              <h3>Ciphertext (Output)</h3>
              <span class="matrix-badge">Hasil enkripsi</span>
            </div>
            <HexMatrix
              :matrix="ciphertextMatrix"
              title="Ciphertext (Column-Major)"
            />
          </AppCard>
        </div>

        <!-- Tab: Round Keys -->
        <div v-else-if="activeTab === 'keys' && roundKeys" class="aes-lab-panel">
          <AppCard padding="md" class="aes-lab-matrix-card">
            <div class="matrix-header">
              <h3>Original Key (16 byte)</h3>
            </div>
            <HexMatrix
              :matrix="originalKeyMatrix"
              title="Kunci Asli"
            />
          </AppCard>

          <AppCard padding="md" class="aes-lab-matrix-card" v-for="(rk, i) in (roundKeys?.round_keys ?? []).slice(1)" :key="i">
            <div class="matrix-header">
              <h3>Round Key {{ i + 1 }}</h3>
            </div>
            <HexMatrix
              :matrix="rk"
              title="Round Key"
:highlights="getKeyExpansionHighlights().filter(h => h.wordIndex >= i * 4 && h.wordIndex < (i + 1) * 4).map(h => ({
                  row: Math.floor(h.wordIndex / 4),
                  col: h.wordIndex % 4,
                  type: h.type
                }))"
            />
          </AppCard>

          <AppCard padding="md" class="aes-lab-legend-card">
            <h3>Keterangan Highlight</h3>
            <div class="legend-grid">
              <div class="legend-item">
                <span class="legend-color" style="background: var(--color-warning)"></span>
                <span>RotWord</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background: var(--color-primary)"></span>
                <span>SubWord</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background: var(--color-error)"></span>
                <span>Rcon</span>
              </div>
            </div>
            <p class="legend-note">
              Key expansion mengikuti standar FIPS-197. Setiap round key 16 byte (4 word).
              Word ke-4, 8, 12... melewati RotWord → SubWord → XOR dengan Rcon.
            </p>
          </AppCard>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.aes-lab-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.aes-lab-header {
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

.aes-lab-title {
  font-size: var(--text-section);
  margin: 0;
  flex: 1;
  text-align: center;
}

.aes-lab-main {
  flex: 1;
  padding: var(--space-6) var(--container-padding);
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

.aes-lab-tabs-card {
  margin-bottom: var(--space-4);
}

.aes-lab-tabs {
  display: flex;
  gap: var(--space-1);
  background-color: var(--color-background);
  border-radius: var(--radius-md);
  padding: var(--space-1);
}

.aes-lab-tab {
  flex: 1;
  padding: var(--space-2) var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: 500;
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.aes-lab-tab:hover {
  color: var(--color-text-primary);
}

.aes-lab-tab--active {
  color: white;
  background-color: var(--color-primary);
}

.aes-lab-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  gap: var(--space-4);
  color: var(--color-text-secondary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.aes-lab-error {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-error);
}

.aes-lab-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.aes-lab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.aes-lab-matrix-card {
  width: 100%;
}

.matrix-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.matrix-header h3 {
  margin: 0;
  font-size: var(--text-subhead);
}

.matrix-badge {
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  background-color: var(--color-background);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-pill);
}

.round-stages {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.round-stages__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.aes-lab-legend-card {
  width: 100%;
}

.aes-lab-legend-card h3 {
  margin: 0 0 var(--space-3);
  font-size: var(--text-subhead);
}

.legend-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-3);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-text-secondary);
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-sm);
}

.legend-note {
  margin: 0;
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  line-height: 1.6;
}

@media (max-width: 640px) {
  .aes-lab-main {
    padding: var(--space-4);
  }
  .round-stages__row {
    grid-template-columns: 1fr;
  }
}
</style>