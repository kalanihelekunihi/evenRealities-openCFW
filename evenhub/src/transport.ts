// 0xAA multipart transport (stock platform\protocols\transport_protocol\transport_protocol.c,
// TPL_SendPacket 0x004B9640 / TPL_ReceivePacket 0x004B910C; reconstruction in
// g2/src/apollo-main/app/a-19-transport-protocol/transport_protocol_rx.c).
//
//   [0] 0xAA  [1] src (low nibble) | dst (high nibble)  [2] syncId
//   [3] data length of this packet (final packet includes the 2-byte CRC)
//   [4] packetTotalNum  [5] packetNum (1-based)  [6] serviceId
//   [7] flags: bit5 = sender wants a sync result, bits1..4 = tplRet (status) in responses
//   [8..] data; CRC-16/CCITT-FALSE over the whole reassembled payload, LE, after the last packet.
import { crc16CcittFalse } from './crc16.ts';

export const TPL_MAGIC = 0xaa;
export const TPL_HEADER_LEN = 8;
export const TPL_MAX_PAYLOAD = 0x1000; // stock static 4 KiB send buffer
export const TPL_ATT_OVERHEAD = 11;    // ATT write header (3) + TPL header (8)
export const FLAG_SYNC = 0x20;

export const NODE_PHONE = 1;
export const NODE_GLASSES = 2;

export type TplHeader = {
  src: number; dst: number; syncId: number; total: number; index: number;
  serviceId: number; flags: number;
};

export type TplMessage = TplHeader & { payload: Uint8Array };

export function maxPacketData(attMtu: number): number {
  // header byte [3] is a u8, so a packet never carries more than 255 data bytes.
  return Math.min(255, attMtu - TPL_ATT_OVERHEAD);
}

/** Split one service payload into ready-to-write ATT values. */
export function encodeMessage(
  m: { serviceId: number; syncId: number; payload: Uint8Array; flags?: number; src?: number; dst?: number },
  attMtu = 247,
): Uint8Array[] {
  const { payload } = m;
  if (payload.length > TPL_MAX_PAYLOAD) throw new RangeError(`payload ${payload.length} > ${TPL_MAX_PAYLOAD}`);
  const cap = maxPacketData(attMtu);
  if (cap < 3) throw new RangeError(`ATT MTU ${attMtu} too small`);
  const crc = crc16CcittFalse(payload);
  const body = new Uint8Array(payload.length + 2);
  body.set(payload); body[payload.length] = crc & 0xff; body[payload.length + 1] = crc >> 8;
  // Chunk payload+CRC; the CRC must sit wholly inside the final packet, so if the
  // last chunk would hold a single byte, borrow one byte from the previous chunk.
  const sizes: number[] = [];
  for (let off = 0; off < body.length; off += cap) sizes.push(Math.min(cap, body.length - off));
  if (sizes.length > 1 && sizes[sizes.length - 1] < 2) { sizes[sizes.length - 2] -= 1; sizes[sizes.length - 1] += 1; }
  const total = sizes.length;
  if (total > 255) throw new RangeError('too many packets');
  const out: Uint8Array[] = [];
  let off = 0;
  sizes.forEach((n, k) => {
    const pkt = new Uint8Array(TPL_HEADER_LEN + n);
    pkt[0] = TPL_MAGIC;
    pkt[1] = ((m.dst ?? NODE_GLASSES) << 4) | ((m.src ?? NODE_PHONE) & 0xf);
    pkt[2] = m.syncId & 0xff; pkt[3] = n; pkt[4] = total; pkt[5] = k + 1;
    pkt[6] = m.serviceId & 0xff; pkt[7] = (m.flags ?? FLAG_SYNC) & 0xff;
    pkt.set(body.subarray(off, off + n), TPL_HEADER_LEN);
    out.push(pkt); off += n;
  });
  return out;
}

export function parseHeader(p: Uint8Array): TplHeader {
  if (p.length < TPL_HEADER_LEN) throw new Error('tpl: short packet');
  if (p[0] !== TPL_MAGIC) throw new Error('tpl: bad magic');
  return { src: p[1] & 0xf, dst: p[1] >> 4, syncId: p[2], total: p[4], index: p[5], serviceId: p[6], flags: p[7] };
}

type Ctx = { h: TplHeader; parts: (Uint8Array | undefined)[]; got: number; timer?: ReturnType<typeof setTimeout> };

/**
 * Reassembler mirroring the firmware RX rules: contexts keyed by service/sync/src/dst,
 * duplicate packets ignored, CRC checked on completion, 1,500 ms inactivity timeout.
 * Header-only (len 0) packets are delivered as control/status frames.
 */
export class Reassembler {
  private ctx = new Map<string, Ctx>();
  private onMessage: (m: TplMessage) => void;
  private onError: (e: Error, h?: TplHeader) => void;
  private timeoutMs: number;
  constructor(onMessage: (m: TplMessage) => void, onError: (e: Error, h?: TplHeader) => void = () => {}, timeoutMs = 1500) {
    this.onMessage = onMessage; this.onError = onError; this.timeoutMs = timeoutMs;
  }

  push(pkt: Uint8Array): void {
    let h: TplHeader;
    try { h = parseHeader(pkt); } catch (e) { this.onError(e as Error); return; }
    const len = pkt[3];
    if (len === 0 && pkt.length === TPL_HEADER_LEN) { this.onMessage({ ...h, payload: new Uint8Array(0) }); return; }
    if (pkt.length < TPL_HEADER_LEN + len) { this.onError(new Error('tpl: truncated'), h); return; }
    if (h.total < 1 || h.index < 1 || h.index > h.total) { this.onError(new Error('tpl: bad index'), h); return; }
    const key = `${h.serviceId}/${h.syncId}/${h.src}/${h.dst}`;
    let c = this.ctx.get(key);
    if (!c || c.parts.length !== h.total) { if (c?.timer) clearTimeout(c.timer); c = { h, parts: new Array(h.total), got: 0 }; this.ctx.set(key, c); }
    if (c.parts[h.index - 1]) return; // duplicate
    c.parts[h.index - 1] = pkt.slice(TPL_HEADER_LEN, TPL_HEADER_LEN + len); c.got++;
    if (c.timer) clearTimeout(c.timer);
    if (c.got < h.total) {
      if (this.timeoutMs > 0) c.timer = setTimeout(() => { this.ctx.delete(key); this.onError(new Error('tpl: rx timeout'), h); }, this.timeoutMs);
      return;
    }
    this.ctx.delete(key);
    const n = c.parts.reduce((a, b) => a + b!.length, 0);
    const all = new Uint8Array(n); let o = 0;
    for (const p of c.parts) { all.set(p!, o); o += p!.length; }
    if (n < 2) { this.onError(new Error('tpl: missing crc'), h); return; }
    const payload = all.subarray(0, n - 2);
    const crc = all[n - 2] | (all[n - 1] << 8);
    if (crc !== crc16CcittFalse(payload)) { this.onError(new Error('tpl: crc mismatch'), h); return; }
    this.onMessage({ ...c.h, payload });
  }

  reset(): void { for (const c of this.ctx.values()) if (c.timer) clearTimeout(c.timer); this.ctx.clear(); }
}
