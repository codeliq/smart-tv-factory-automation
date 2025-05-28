<template>
  <div class="chart-container">
    <h3>🧱 최근 작업 스택</h3>
    <div class="task-box">
      <div
        v-for="(task, index) in taskStack"
        :key="index"
        class="task-item"
        :style="{ backgroundColor: getColor(task.task) }"
      >
        {{ task.task }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskStackChart',
  props: {
    taskStack: {
      type: Array,
      required: true
    }
  },
  methods: {
    getColor(task) {
      if (task.includes('픽업')) return '#3B5BDB'; // 연보라
      if (task.includes('이동')) return '#db86a4'; // 연핑크
      return '#6eb589'; // 밝은 노랑 (분류)
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.task-box {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.task-item {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  color: white;
  font-weight: bold;
  min-width: 80px;
  transition: background-color 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
}
</style>
