<script setup lang="ts">
import { computed } from 'vue'
interface Props {
  secondsLeft: number
  warningThreshold?: number
}

const props = withDefaults(defineProps<Props>(), {
  warningThreshold: 30,
})

const colorClass = computed(() => {
  if (props.secondsLeft <= 10) return 'timer-indicator--critical'
  if (props.secondsLeft <= props.warningThreshold) return 'timer-indicator--warning'
  return ''
})

const formattedTime = computed(() => {
  const mins = Math.floor(props.secondsLeft / 60)
  const secs = props.secondsLeft % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
})
</script>

<template>
  <span
    class="timer-indicator"
    :class="colorClass"
    :aria-live="props.secondsLeft <= props.warningThreshold ? 'polite' : 'off'"
    :aria-label="`Sisa waktu kunci otomatis: ${formattedTime}`"
  >
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </svg>
    {{ formattedTime }}
  </span>
</template>

<style scoped>
.timer-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-mono);
  font-size: var(--text-small);
  font-variant-numeric: tabular-nums;
  color: var(--color-text-secondary);
  transition: color var(--transition-fast);
}

.timer-indicator--warning {
  color: var(--color-warning);
}

.timer-indicator--critical {
  color: var(--color-error);
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>