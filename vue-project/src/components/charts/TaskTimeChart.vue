<template>
  <div class="chart-container">
    <h3>작업 시간 시각화</h3>
    <BarChart :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
)

export default {
  name: 'TaskTimeChart',
  components: {
    BarChart: Bar
  },
  props: {
    taskTimes: {
      type: Array,
      required: true
    },
    taskLabels: {
      type: Array,
      required: true
    }
  },
  computed: {
    chartData() {
      return {
        labels: this.taskLabels,
        datasets: [
          {
            label: '작업 시간 (sec)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
            data: this.taskTimes
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        plugins: {
          legend: {
            position: 'top'
          },
          title: {
            display: true,
            text: '작업 변화 시각화'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
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
