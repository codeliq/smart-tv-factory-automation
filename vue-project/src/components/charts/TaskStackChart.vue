<template>
  <div class="chart-container">
    <h3>🧱 최근 작업 스택</h3>
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'TaskStackChart',
  components: { Bar },
  props: {
    taskStack: {
      type: Array,
      required: true
    }
  },
  computed: {
    chartData() {
      return {
        labels: this.taskStack.map(item => item.task),
        datasets: [
          {
            label: '작업 시간 (초)',
            data: this.taskStack.map(item => item.time),
            backgroundColor: this.taskStack.map(item => {
              if (item.task.includes('픽업')) return 'rgba(54, 162, 235, 0.6)'
              if (item.task.includes('이동')) return 'rgba(255, 206, 86, 0.6)'
              return 'rgba(255, 99, 132, 0.6)' // 분류 등
            }),
            borderColor: 'rgba(0,0,0,0.1)',
            borderWidth: 1
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: { display: true, text: '최근 작업 스택 시각화' }
        },
        scales: {
          y: { beginAtZero: true },
          x: { ticks: { autoSkip: false } }
        }
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}
</style>