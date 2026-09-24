<script setup lang="ts">
interface Props {
  note: {
    id: string
    title: string
    updated_at: string
  }
}

const props = defineProps<Props>()
const emit = defineEmits<{ click: [id: string] }>()

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div
    class="note-card"
    @click="$emit('click', note.id)"
    tabindex="0"
    @keydown.enter="$emit('click', note.id)"
    @keydown.space.prevent="$emit('click', note.id)"
    role="button"
    :aria-label="`Buka catatan: ${note.title}`"
  >
    <div class="note-card__content">
      <h3 class="note-card__title">{{ note.title }}</h3>
      <time class="note-card__date" :dateTime="note.updated_at">
        {{ formatDate(note.updated_at) }}
      </time>
    </div>
    <svg class="note-card__chevron" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <path d="M9 18l6-6-6-6" />
    </svg>
  </div>
</template>

<style scoped>
.note-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition:
    transform var(--transition-base),
    box-shadow var(--transition-base),
    border-color var(--transition-base);
}

.note-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover);
  border-color: var(--color-primary);
}

.note-card:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus);
  border-color: var(--color-primary);
}

.note-card__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.note-card__title {
  margin: 0;
  font-size: var(--text-body);
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-card__date {
  margin: 0;
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.note-card__chevron {
  flex-shrink: 0;
  color: var(--color-neutral);
  transition: color var(--transition-fast);
}

.note-card:hover .note-card__chevron {
  color: var(--color-primary);
}
</style>