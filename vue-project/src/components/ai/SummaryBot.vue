<template>
  <div class="chat-button" @click="toggleChat">💬 요약 받기</div>

  <div class="chat-popup" v-if="chatVisible">
    <div class="chat-header">
      <span>📌 AI 작업 요약</span>
      <button @click="toggleChat">✖</button>
    </div>

    <div class="chat-body">
      <div class="chat-response" v-if="loading">요약 중입니다...</div>
      <div class="chat-response" v-else-if="response">{{ response }}</div>
      <div class="chat-response" v-else>최근 작업 요약이 여기에 표시됩니다.</div>
    </div>

    <div class="chat-footer">
      <button @click="summarizeLogs">📄 요약 요청</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "SummaryBot",
  props: {
    logs: Array, // Dashboard에서 최근 작업 로그 배열을 props로 받음
  },
  data() {
    return {
      chatVisible: false,
      loading: false,
      response: "",
    };
  },
  methods: {
    toggleChat() {
      this.chatVisible = !this.chatVisible;
    },
    async summarizeLogs() {
      this.loading = true;
      const logText = this.logs.map((log) => `- ${log.time} ${log.desc}`).join("\n");

      try {
        const logText = this.logs.map((log) => `- ${log.time} ${log.desc}`).join("\n");

        const res = await fetch("http://localhost:3001/summarize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ logs: logText }),
        });

        const data = await res.json();
        this.response = data.summary;
      } catch (err) {
        this.response = "요약 요청에 실패했습니다.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.chat-button {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: #6366f1;
  color: white;
  padding: 0.75rem 1.25rem;
  border-radius: 1.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  font-weight: bold;
}

.chat-popup {
  position: fixed;
  bottom: 5rem;
  right: 2rem;
  width: 280px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 0.75rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 1000;
}

.chat-header {
  background: #6366f1;
  color: white;
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.chat-body {
  padding: 1rem;
  max-height: 200px;
  overflow-y: auto;
  font-size: 0.9rem;
  color: #333;
}

.chat-footer {
  padding: 0.75rem;
  text-align: right;
  border-top: 1px solid #eee;
}

.chat-footer button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.85rem;
}
</style>
