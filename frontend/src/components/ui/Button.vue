<template>
    <button 
      :class="[
        'px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2',
        variantClasses,
        sizeClasses,
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      ]"
      :disabled="disabled"
      v-bind="$attrs"
    >
      <div class="flex items-center gap-2">
        <component v-if="icon" :is="icon" class="h-4 w-4" />
        <slot></slot>
      </div>
    </button>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  
  const props = defineProps({
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'danger'].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg'].includes(value)
    },
    icon: {
      type: Object,
      default: null
    },
    disabled: {
      type: Boolean,
      default: false
    }
  })
  
  const variantClasses = computed(() => ({
    primary: 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500'
  }[props.variant]))
  
  const sizeClasses = computed(() => ({
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  }[props.size]))
  </script>