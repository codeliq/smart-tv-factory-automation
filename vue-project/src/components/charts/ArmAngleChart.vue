<template>
  <div class="chart-container">
    <h3>🦾로봇 관절 모니터링</h3>
    <div v-if="angles && angles.length > 0" class="grid-wrapper">
      <div v-for="(angle, index) in angles" :key="index" class="angle-chart-item">
        <Doughnut :data="getChartData(index, angle)" :options="getChartOptions(index, angle)" />
        <p class="angle-label">관절{{ index + 1 }}: {{ angle }}°</p>
      </div>
    </div>
    <div v-else>
      <p>차트 데이터를 불러오는 중...</p>
    </div>
  </div>
</template>

<script>
import { Doughnut } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, ArcElement);

export default {
  name: 'ArmAngleChart',
  components: {
    Doughnut
  },
  props: {
    angles: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getChartData(index, angle) {
      const normalizedAngle = Math.max(0, Math.min(360, angle + 180));
      return {
        labels: ['각도', '나머지'],
        datasets: [
          {
            label: `관절 ${index + 1}`,
            data: [normalizedAngle, 360 - normalizedAngle],
            backgroundColor: [
              'rgba(60, 100, 231, 0.7)',
              'rgba(220, 220, 220, 0.2)'
            ],
            borderWidth: 1,
            cutout: '70%'
          }
        ]
      };
    },
    getChartOptions(index, angle) {
      return {
        responsive: true,
        plugins: {
          legend: { display: false }
        }
      };
    }
  }
};
</script>

<style scoped>
.chart-container {
  width: 100%;
  margin: 1rem auto;
}

.grid-wrapper {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 2개씩 가로로 */
  gap: 1.5rem;
  justify-items: center;
  align-items: center;
}

.angle-chart-item {
  width: 160px;
  height: 230px;
  text-align: center;
}

.angle-label {
  margin-top: 0.5rem;
  font-weight: bold;
  color: #1e293b;
}
</style>
