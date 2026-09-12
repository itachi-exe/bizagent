// Baileys shim — bridges a WhatsApp Web session to the FastAPI backend.
// Scope: normalize incoming text messages, forward them, and relay outgoing sends.
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const express = require('express');
const qrcode = require('qrcode-terminal');
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');

const INTERNAL_BASE = `http://localhost:${process.env.BAILEYS_INTERNAL_PORT || 8000}`;
const OWNER_PHONE_NUMBER = process.env.OWNER_PHONE_NUMBER || '';
const SHIM_PORT = new URL(process.env.BAILEYS_SHIM_URL || 'http://localhost:8002').port || 8002;

let sock;

async function startBaileys() {
  const { state, saveCreds } = await useMultiFileAuthState('./baileys_auth');
  sock = makeWASocket({ auth: state });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update;
    if (qr) qrcode.generate(qr, { small: true });
    if (connection === 'close') {
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
      console.log('Connection closed. Reconnecting:', shouldReconnect);
      if (shouldReconnect) startBaileys();
    } else if (connection === 'open') {
      console.log('Baileys connected.');
    }
  });

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;
    for (const msg of messages) {
      if (msg.key.fromMe) continue;
      const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text;
      if (!text) continue; // drop media, reactions, status updates — text only

      const phoneNumber = msg.key.remoteJid.replace('@s.whatsapp.net', '');
      const payload = {
        message_id: msg.key.id,
        from: msg.key.remoteJid,
        phone_number: phoneNumber,
        display_name: msg.pushName || null,
        text,
        timestamp: Number(msg.messageTimestamp),
      };

      const isOwnerCommand = phoneNumber === OWNER_PHONE_NUMBER && text.startsWith('/deliver');
      const path = isOwnerCommand ? '/internal/owner-command' : '/internal/message';
      const body = isOwnerCommand ? { from: payload.from, text } : payload;

      try {
        await fetch(`${INTERNAL_BASE}${path}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
      } catch (err) {
        console.error('Failed to forward message to FastAPI:', err.message);
      }
    }
  });
}

const app = express();
app.use(express.json());

// Must ACK the caller fast — fire the WhatsApp send without blocking the response.
app.post('/send', (req, res) => {
  const { to, text } = req.body;
  res.sendStatus(200);
  if (!sock) return console.error('Send requested before Baileys connected');
  sock.sendMessage(to, { text }).catch((err) => console.error('sendMessage failed:', err.message));
});

app.listen(SHIM_PORT, () => console.log(`Baileys shim listening on :${SHIM_PORT}`));

startBaileys();
