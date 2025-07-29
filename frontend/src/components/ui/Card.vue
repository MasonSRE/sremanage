<template>
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="$slots.header" class="px-6 py-4 border-b border-gray-200">
        <slot name="header"></slot>
      </div>
      <div class="px-6 py-4">
        <slot></slot>
      </div>
      <div v-if="$slots.footer" class="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <slot name="footer"></slot>
      </div>
    </div>
  </template>