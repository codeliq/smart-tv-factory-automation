<template>
  <h3>📦 인식된 보드 요약</h3>
  <div class="board-stats">
    <p><strong>총 보드 수:</strong> {{ total }}</p>
    <p><strong>🔵 파랑:</strong> {{ blue }}</p>
    <p><strong>⚪ 흰색:</strong> {{ white }}</p>
    <p><strong>🔴 빨강 (불량):</strong> {{ red }}</p>
    <p><strong>❌ 불량 누적합:</strong> {{ red }}</p>
  </div>
</template>

<script>
export default {
  name: "BoardStats",
  props: {
    total: {
      type: Number,
      required: true,
    },
    blue: {
      type: Number,
      required: true,
    },
    white: {
      type: Number,
      required: true,
    },
    red: {
      type: Number,
      required: true,
    },
  },
};
</script>

<style scoped>
.board-stats {
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-top: 1rem;
}

.board-summary p {
  margin: 0.4rem 0;
  font-size: 1rem;
}
</style>
