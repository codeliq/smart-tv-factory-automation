// 예시: WebSocket을 통한 실시간 데이터 수신
import { ref } from 'vue';

const robotData = ref(null);

const socket = new WebSocket('ws://your-robot-api-endpoint');

socket.onmessage = (event) => {
  robotData.value = JSON.parse(event.data);
};

export default {
  robotData,
};
