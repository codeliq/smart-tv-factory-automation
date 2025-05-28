<template>
  <div class="position-map">
    <h3>📍 로봇 현재 위치</h3>
    <canvas ref="canvas" width="400" height="400"></canvas>
  </div>
</template>

<script>
export default {
  name: 'PositionMap',
  props: {
    position: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      path: []  // 이동 경로 누적 저장
    };
  },
  watch: {
    position(newPos) {
      this.path.push({ x: newPos.x, y: newPos.y });
      this.drawPath();
    }
  },
  mounted() {
    this.ctx = this.$refs.canvas.getContext('2d');
  },
  methods: {
    drawPath() {
      const ctx = this.ctx;
      if (!ctx || this.path.length === 0) return;

      ctx.clearRect(0, 0, 400, 400); // 전체 초기화

      // 선 그리기
      ctx.beginPath();
      this.path.forEach((p, index) => {
        if (index === 0) {
          ctx.moveTo(p.x, p.y);
        } else {
          ctx.lineTo(p.x, p.y);
        }
      });
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.stroke();

      // 현재 위치 점 표시
      const last = this.path[this.path.length - 1];
      ctx.beginPath();
      ctx.arc(last.x, last.y, 5, 0, 2 * Math.PI);
      ctx.fillStyle = '#ef4444';
      ctx.fill();
    }
  }
};
</script>

<style scoped>
.position-map {
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
</style>
