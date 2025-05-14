<script setup>
const props = defineProps({
    parentTitle: String,
    subParentTitle: String
})
</script>

<template>
  <div class="breadcrumb border-b border-gray-300 mb-2">
    <ul class="flex items-center text-sm text-gray-500 space-x-1 pt-2 pb-2">
      <li class="border-r border-gray-400 pr-2 dark:text-gray-400 font-semibold">
        <a class="hover:text-gray-800" href="#">{{ props.parentTitle }}</a>
      </li>
      <li class="pl-2 dark:text-gray-400 font-semibold">
        {{ props.subParentTitle }}
      </li>
    </ul>
  </div>
</template>

