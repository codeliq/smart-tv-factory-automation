const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const bodyParser = require('body-parser');
const OpenAI = require('openai');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(cors());
app.use(bodyParser.json());

let latestRobotData = null;

// OpenAI 초기화
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// 로봇 상태 WebSocket으로 전송
function broadcastToClients(data) {
  const json = JSON.stringify(data);
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(json);
    }
  });
}

// 로봇 상태 업데이트 API
app.post('/update-status', (req, res) => {
  const data = req.body;
  console.log('[RECEIVED]', data);
  latestRobotData = data;
  broadcastToClients(data);
  res.status(200).send({ message: 'Data received and broadcasted' });
});

// 최신 상태 조회 API
app.get('/latest', (req, res) => {
  res.json(latestRobotData || { message: 'No data received yet' });
});

// 작업 로그 요약 API
app.post('/summarize', async (req, res) => {
  const { logs } = req.body;

  if (!logs || typeof logs !== 'string') {
    return res.status(400).json({ summary: '로그 형식이 잘못되었습니다.' });
  }

  try {
    // const prompt = `다음 작업 로그를 읽고 간결하게 요약해 주세요:\n\n${logs}`;
    // const completion = await openai.chat.completions.create({
    //   model: 'gpt-4o-mini', // 또는 'gpt-4o'
    //   messages: [{ role: 'user', content: prompt }],
    //   temperature: 0.7,
    // });

      const prompt = `
      다음은 로봇의 최근 작업 로그입니다:
      ${logs}

      위 내용을 간단히 요약해 주세요. 예: 불량 비율, 주요 이벤트, 전체 작업 개요 등.
      `.trim();

      const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',  // 또는 'gpt-4', 'gpt-3.5-turbo'
      messages: [
        {
          role: 'system',
          content: '당신은 스마트 공정 요약을 잘하는 AI입니다.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.7,
    });
    const summary = completion.choices[0].message.content.trim();

    // 터미널에 요약 결과 출력
    console.log('[요약 결과]', summary);

    res.json({ summary });

  } catch (error) {
    console.error('[OpenAI 요약 에러]', error.message);
    res.status(500).json({ summary: '요약 요청에 실패했습니다.' });
  }
});

// WebSocket 연결 처리
wss.on('connection', (ws) => {
  console.log('[WS] 클라이언트 WebSocket 연결됨');
  if (latestRobotData) {
    ws.send(JSON.stringify(latestRobotData));
  }
});

// 서버 실행
const PORT = 3001;
server.listen(PORT, () => {
  console.log(`[SERVER] 🚀 서버 실행 중: http://localhost:${PORT}`);
});
