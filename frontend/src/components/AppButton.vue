<script setup lang="ts">
import { computed } from 'vue'
interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  type: 'button',
})

const classNames = computed(() => [
  'app-button',
  `app-button--${props.variant}`,
  `app-button--${props.size}`,
  { 'app-button--disabled': props.disabled, 'app-button--loading': props.loading },
])

const handleClick = (event: MouseEvent) => {
  if (props.disabled || props.loading) {
    event.preventDefault()
    event.stopPropagation()
    return
  }
}
</script>

<template>
  <button
    :type="type"
    :class="classNames"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="app-button__spinner" aria-hidden="true">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" stroke-opacity="0.25" />
        <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round" />
      </svg>
    </span>
    <slot />
  </button>
</template>

<style scoped>
.app-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-body);
  font-weight: 500;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition:
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    color var(--transition-fast);
  white-space: nowrap;
  user-select: none;
}

.app-button:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus);
}

.app-button--disabled,
.app-button--loading {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.app-button:not(.app-button--disabled):not(.app-button--loading):hover {
  transform: translateY(-1px);
}

.app-button:not(.app-button--disabled):not(.app-button--loading):active {
  transform: translateY(0);
}

/* Sizes */
.app-button--sm {
  height: 32px;
  padding: 0 var(--space-3);
  font-size: var(--text-small);
}

.app-button--md {
  height: 38px;
  padding: 0 var(--space-4);
  font-size: var(--text-body);
}

.app-button--lg {
  height: 44px;
  padding: 0 var(--space-5);
  font-size: var(--text-body);
}

/* Variants */
.app-button--primary {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.app-button--primary:hover:not(.app-button--disabled) {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
  box-shadow: var(--shadow-button-hover);
}

.app-button--secondary {
  background-color: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.app-button--secondary:hover:not(.app-button--disabled) {
  background-color: rgba(99, 102, 241, 0.08);
}

.app-button--ghost {
  background-color: transparent;
  color: var(--color-text-primary);
  border-color: transparent;
}

.app-button--ghost:hover:not(.app-button--disabled) {
  background-color: var(--color-border);
  color: var(--color-text-primary);
}

.app-button--destructive {
  background-color: transparent;
  color: var(--color-error);
  border-color: var(--color-error);
}

.app-button--destructive:hover:not(.app-button--disabled) {
  background-color: rgba(239, 68, 68, 0.08);
}

/* Spinner */
.app-button__spinner {
  display: inline-flex;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>