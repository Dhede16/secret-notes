<script setup lang="ts">
interface Props {
  modelValue: string
  type?: 'text' | 'password' | 'email' | 'number'
  placeholder?: string
  error?: string
  label?: string
  disabled?: boolean
  required?: boolean
  textarea?: boolean
  rows?: number
  autocomplete?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  required: false,
  textarea: false,
  rows: 4,
  autocomplete: 'off',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

const inputId = `input-${Math.random().toString(36).slice(2)}`
const errorId = `${inputId}-error`

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="app-input-wrapper">
    <label v-if="label" :for="inputId" class="app-input__label">
      {{ label }}
    </label>
    <div class="app-input__container" :class="{ 'app-input__container--error': error, 'app-input__container--disabled': disabled }">
      <input
        v-if="!textarea"
        :id="inputId"
        :type="type"
        :placeholder="placeholder"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        :aria-invalid="!!error"
        :aria-describedby="error ? errorId : undefined"
        @input="handleInput"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
        class="app-input"
      />
      <textarea
        v-else
        :id="inputId"
        :placeholder="placeholder"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :rows="rows"
        :aria-invalid="!!error"
        :aria-describedby="error ? errorId : undefined"
        @input="handleInput"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
        class="app-input app-input--textarea"
      />
    </div>
    <p v-if="error" :id="errorId" class="app-input__error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.app-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  width: 100%;
}

.app-input__label {
  font-size: var(--text-small);
  font-weight: 500;
  color: var(--color-text-primary);
}

.app-input__container {
  position: relative;
  display: flex;
  align-items: center;
}

.app-input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-body);
  font-family: var(--font-body);
  color: var(--color-text-primary);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.app-input::placeholder {
  color: var(--color-neutral);
}

.app-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: var(--shadow-focus);
}

.app-input:disabled {
  background-color: var(--color-background);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.app-input__container--error .app-input {
  border-color: var(--color-error);
}

.app-input__container--error .app-input:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.12);
}

.app-input--textarea {
  min-height: 100px;
  resize: vertical;
  line-height: 1.6;
}

.app-input__error {
  margin: 0;
  font-size: var(--text-caption);
  color: var(--color-error);
}
</style>