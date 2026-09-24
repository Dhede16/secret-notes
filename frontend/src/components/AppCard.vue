<script setup lang="ts">
interface Props {
  hoverable?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
  bordered?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: false,
  padding: 'md',
  bordered: true,
})

const paddingClasses = {
  none: '',
  sm: 'app-card--padding-sm',
  md: 'app-card--padding-md',
  lg: 'app-card--padding-lg',
}
</script>

<template>
  <div
    :class="[
      'app-card',
      { 'app-card--hoverable': hoverable, 'app-card--bordered': bordered },
      paddingClasses[padding],
    ]"
  >
    <slot />
  </div>
</template>

<style scoped>
.app-card {
  background-color: var(--color-surface);
  border-radius: var(--radius-xl);
  transition:
    transform var(--transition-base),
    box-shadow var(--transition-base);
}

.app-card--bordered {
  border: 1px solid var(--color-border);
}

.app-card--hoverable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover);
}

.app-card--padding-none {
  padding: 0;
}

.app-card--padding-sm {
  padding: var(--space-3);
}

.app-card--padding-md {
  padding: var(--space-4);
}

.app-card--padding-lg {
  padding: var(--space-6);
}
</style>