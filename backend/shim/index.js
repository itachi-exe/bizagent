require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const express = require('express');
const qrcode = require('qrcode-terminal');
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, delay } = require('@whiskeysockets/baileys');
const fs = require('fs');

const INTERNAL_BASE = `http://localhost:${process.env.BAILEYS_INTERNAL_PORT || 8000}`;
const OWNER_PHONE_NUMBER = process.env.OWNER_PHONE_NUMBER || '';
const SHIM_PORT = new URL(process.env.BAILEYS_SHIM_URL || 'http://localhost:8002').port || 8002;

let sock;
let isConnected = false;
let sendQueue = []; // buffer sends while reconnecting

async function flushQueue() {
  while (sendQueue.length > 0 && isConnected) {
    const { to, text, resolve } = sendQueue.shift();
    try {
      await sock.sendMessage(to, { text });
      console.log(`[SEND OK] to=${to}`);
      resolve(true);
    } catch (err) {
      console.error(`[SEND FAIL] to=${to} err=${err.message}`);
      resolve(false);
    }
  }
}

async function sendMessage(to, text) {
  return new Promise((resolve) => {
    if (isConnected && sock) {
      sock.sendMessage(to, { text })
        .then(() => { console.log(`[SEND OK] to=${to}`); resolve(true); })
        .catch((err) => { console.error(`[SEND FAIL] to=${to} err=${err.message}`); resolve(false); });
    } else {
      console.log(`[SEND QUEUED] to=${to} — not connected yet`);
      sendQueue.push({ to, text, resolve });
      // resolve false after 10s if still not connected
      setTimeout(() => resolve(false), 10000);
    }
  });
}

async function startBaileys() {
  const { state, saveCreds } = await useMultiFileAuthState('./baileys_auth');
  sock = makeWASocket({
    auth: state,
    connectTimeoutMs: 60000,
    defaultQueryTimeoutMs: 60000,
    keepAliveIntervalMs: 15000,
    retryRequestDelayMs: 3000,
    generateHighQualityLinkPreview: false,
    syncFullHistory: false,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;
    if (qr) {
      qrcode.generate(qr, { small: true });
      fs.writeFileSync('/tmp/baileys_qr.txt', qr);
      console.log('QR_READY');
    }
    if (connection === 'close') {
      isConnected = false;
      const code = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = code !== DisconnectReason.loggedOut;
      console.log(`[CONN CLOSED] code=${code} reconnect=${shouldReconnect}`);
      if (shouldReconnect) {
        await delay(3000);
        startBaileys();
      }
    } else if (connection === 'open') {
      isConnected = true;
      console.log('Baileys connected.');
      flushQueue();
    }
  });

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;
    for (const msg of messages) {
      if (msg.key.fromMe) continue;
      const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text;
      if (!text) continue;

      const jid = msg.key.remoteJidAlt || msg.key.remoteJid;
      const phoneNumber = jid.replace('@s.whatsapp.net', '').replace('@lid', '');
      console.log(`[INBOUND] from=${phoneNumber} text="${text}"`);

      const payload = {
        message_id: msg.key.id,
        from: jid,
        phone_number: phoneNumber,
        display_name: msg.pushName || null,
        text,
        timestamp: Number(msg.messageTimestamp),
      };

      const isOwnerCommand = phoneNumber === OWNER_PHONE_NUMBER && text.startsWith('/deliver');
      const path = isOwnerCommand ? '/internal/owner-command' : '/internal/message';
      const body = isOwnerCommand ? { from: payload.from, text } : payload;

      try {
        const resp = await fetch(`${INTERNAL_BASE}${path}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        console.log(`[FORWARD] ${path} → ${resp.status}`);
      } catch (err) {
        console.error(`[FORWARD FAIL] ${err.message}`);
      }
    }
  });
}

const app = express();
app.use(express.json());

app.post('/send', async (req, res) => {
  const { to, text } = req.body;
  res.sendStatus(200); // ACK immediately
  const ok = await sendMessage(to, text);
  if (!ok) console.error(`[SEND] delivery failed for ${to}`);
});

app.post('/send-voice', async (req, res) => {
  const { to, audio_path } = req.body;
  if (!to || !audio_path) return res.status(400).json({ error: 'missing to or audio_path' });
  res.sendStatus(200);
  try {
    const buf = fs.readFileSync(audio_path);
    await sock.sendMessage(to, { audio: buf, mimetype: 'audio/ogg; codecs=opus', ptt: true });
    console.log(`[VOICE OK] to=${to}`);
  } catch (err) {
    console.error(`[VOICE FAIL] to=${to} err=${err.message}`);
  }
});

app.listen(SHIM_PORT, () => console.log(`Baileys shim listening on :${SHIM_PORT}`));
startBaileys();
