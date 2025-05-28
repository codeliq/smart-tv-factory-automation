<template>
  <img :src="streamUrl" alt="Camera Stream" />
</template>

<script>
export default {
  name: "CameraStream",
  data() {
    return {
      streamUrl: "http://localhost:5000/video_feed", // Flask 서버 주소
    };
  },
};
</script>

<style scoped>
.camera-container {
  border: 1px solid #ccc;
  padding: 1rem;
  background-color: #fff;
}
img {
  width: 100%;
  max-width: 640px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
