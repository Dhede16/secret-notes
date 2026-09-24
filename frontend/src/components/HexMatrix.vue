<script setup lang="ts">
import { computed } from 'vue'
interface Props {
  matrix: number[][]
  highlights?: Array<{
    row: number
    col: number
    type: 'rotword' | 'subword' | 'rcon'
  }>
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  highlights: () => [],
})

const highlightMap = computed(() => {
  const map = new Map<string, 'rotword' | 'subword' | 'rcon'>()
  props.highlights.forEach((h) => {
    map.set(`${h.row},${h.col}`, h.type)
  })
  return map
})

function getCellClass(row: number, col: number) {
  const type = highlightMap.value.get(`${row},${col}`)
  if (!type) return ''
  return `hex-matrix__cell--highlight-${type}`
}

function formatByte(byte: number) {
  return byte.toString(16).toUpperCase().padStart(2, '0')
}

function getMatrixValue(row: number, col: number): number {
  return props.matrix[row]?.[col] ?? 0
}
</script>

<template>
  <div class="hex-matrix">
    <div v-if="title" class="hex-matrix__title">{{ title }}</div>
    <div class="hex-matrix__grid" role="table" aria-label="Matriks hexadecimal 4x4">
      <div
        v-for="row in 4"
        :key="row"
        class="hex-matrix__row"
        role="row"
      >
        <div
          v-for="col in 4"
          :key="col"
          :class="['hex-matrix__cell', getCellClass(row - 1, col - 1)]"
          role="gridcell"
          :aria-label="`Baris ${row}, Kolom ${col}: ${formatByte(getMatrixValue(row - 1, col - 1))}`"
        >
          {{ formatByte(getMatrixValue(row - 1, col - 1)) }}
        </div>
      </div>
    </div>
    <div v-if="highlights.length" class="hex-matrix__legend">
      <span class="hex-matrix__legend-item" v-for="item in [
        { type: 'rotword', label: 'RotWord', color: 'var(--color-warning)' },
        { type: 'subword', label: 'SubWord', color: 'var(--color-primary)' },
        { type: 'rcon', label: 'Rcon', color: 'var(--color-error)' },
      ]" :key="item.type">
        <span
          class="hex-matrix__legend-color"
          :style="{ backgroundColor: item.color }"
        />
        {{ item.label }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.hex-matrix {
  font-family: var(--font-mono);
  font-size: var(--text-small);
  line-height: 1;
}

.hex-matrix__title {
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hex-matrix__grid {
  display: inline-grid;
  grid-template-columns: repeat(4, auto);
  gap: var(--space-1);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2);
  background-color: var(--color-surface);
}

.hex-matrix__row {
  display: contents;
}

.hex-matrix__cell {
  width: 2.5ch;
  text-align: center;
  padding: var(--space-1) 0;
  color: var(--color-text-primary);
  background-color: transparent;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

/* Column-major order highlight: AES uses column-major, so highlight by column */
.hex-matrix__cell--highlight-rotword {
  background-color: var(--color-warning);
  color: white;
}

.hex-matrix__cell--highlight-subword {
  background-color: var(--color-primary);
  color: white;
}

.hex-matrix__cell--highlight-rcon {
  background-color: var(--color-error);
  color: white;
}

.hex-matrix__legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-2);
  font-family: var(--font-body);
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
}

.hex-matrix__legend-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
}

.hex-matrix__legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-sm);
}
</style>