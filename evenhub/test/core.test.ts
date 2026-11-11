import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  crc16CcittFalse, encodeMessage, Reassembler, parseHeader, PbWriter, pbFields,
  encodePage, encodeTextUpgrade, encodeImageFragment, decodeMessage, validatePage, EvenHubValidationError,
  encodeBmp4, rleEncode, rleDecode, lz4BlockEncode, lz4BlockDecode, planImage,
  EvenHubClient, Cmd, Compress, type Link, type TplMessage,
} from '../src/index.ts';

const hex = (b: Uint8Array) => Buffer.from(b).toString('hex');

test('crc16 ccitt-false known vector', () => {
  assert.equal(crc16CcittFalse(new TextEncoder().encode('123456789')), 0x29b1);
  assert.equal(crc16CcittFalse(new Uint8Array(0)), 0xffff);
});

test('transport: single packet layout', () => {
  const [p] = encodeMessage({ serviceId: 0xe0, syncId: 7, payload: Uint8Array.of(1, 2, 3) });
  assert.equal(hex(p.subarray(0, 8)), 'aa21070501' + '01e020');
  const crc = crc16CcittFalse(Uint8Array.of(1, 2, 3));
  assert.deepEqual([...p.subarray(8)], [1, 2, 3, crc & 0xff, crc >> 8]);
});

test('transport: fragmentation + reassembly, CRC never split', () => {
  for (const mtu of [23, 247, 512]) for (const len of [0, 1, 233, 234, 235, 236, 1000, 4096]) {
    if (mtu === 23 && len > 255 * 12 - 2) { assert.throws(() => encodeMessage({ serviceId: 0xe0, syncId: 1, payload: new Uint8Array(len) }, mtu)); continue; }
    const payload = Uint8Array.from({ length: len }, (_, i) => (i * 31) & 0xff);
    const pkts = encodeMessage({ serviceId: 0xe0, syncId: 1, payload }, mtu);
    const last = pkts[pkts.length - 1];
    assert.ok(last[3] >= 2, 'last packet carries whole CRC');
    for (const p of pkts) assert.ok(p.length <= mtu - 3, 'fits ATT');
    let got: TplMessage | undefined;
    const r = new Reassembler((m) => (got = m), (e) => assert.fail(e), 0);
    for (const p of [...pkts].reverse()) r.push(p); // out of order
    assert.ok(got); assert.deepEqual([...got!.payload], [...payload]);
  }
});

test('transport: crc mismatch rejected', () => {
  const [p] = encodeMessage({ serviceId: 0xe0, syncId: 1, payload: Uint8Array.of(9, 9) });
  p[8] ^= 1; let err: Error | undefined;
  new Reassembler(() => assert.fail('delivered'), (e) => (err = e), 0).push(p);
  assert.match(err!.message, /crc/);
});

test('transport: payload limit', () => {
  assert.throws(() => encodeMessage({ serviceId: 0xe0, syncId: 1, payload: new Uint8Array(4097) }));
});

test('pb: varint and nested roundtrip', () => {
  const b = new PbWriter().uint(1, 300).uint(2, 0).string(3, 'hi').message(4, new PbWriter().uint(1, 5)).finish();
  assert.equal(hex(b), '08ac021a026869' + '22020805');
  assert.deepEqual([...pbFields(b)].map((f) => f.tag), [1, 3, 4]);
});

test('create page golden encoding follows firmware tags', () => {
  const b = encodePage({ texts: [{ x: 0, y: 0, width: 576, height: 288, containerID: 1, containerName: 't', content: 'Hi', isEventCapture: true }] }, 0x42);
  // root: cmd 0 omitted, magic=0x42 (tag2), oneof tag3 CreateStartUpPage
  // create: tag1 total=1, tag3 text{ w=576(t3) h=288(t4) id=1(t9) name(t10) capture(t11) content(t12) }
  assert.equal(hex(b), '1042' + '1a15' + '0801' + '1a11' + '18c004' + '20a002' + '4801' + '520174' + '5801' + '62024869');
  const rb = encodePage({ images: [{ x: 1, y: 2, width: 20, height: 20, containerID: 3 }] }, 1, true);
  // rebuild: cmd 7, oneof tag 7; image{x=1 y=2 w=20 h=20 id=3}
  assert.equal(hex(rb), '0807' + '1001' + '3a0e' + '0801' + '220a' + '0801' + '1002' + '1814' + '2014' + '2803');
});

test('text upgrade + image fragment cmd/tag pairs', () => {
  const t = encodeTextUpgrade({ containerID: 2, content: 'abc' }, 5);
  let f = [...pbFields(t)];
  assert.deepEqual(f.map((x) => x.tag), [1, 2, Cmd.TextContainerUpgrade.tag]);
  assert.equal(f[0].value, Cmd.TextContainerUpgrade.cmd);
  const i = encodeImageFragment({ containerID: 3, sessionId: 9, totalSize: 4, compressMode: 2, fragmentIndex: 0, data: Uint8Array.of(1, 2, 3, 4) }, 6);
  f = [...pbFields(i)];
  assert.equal(f[0].value, 3); assert.equal(f[2].tag, 5);
  const inner = [...pbFields(f[2].value as Uint8Array)];
  assert.deepEqual(inner.map((x) => x.tag), [1, 3, 4, 5, 7, 8]); // fragmentIndex 0 omitted (proto3)
});

test('validation mirrors firmware rules', () => {
  const t = (id: number, cap = false) => ({ x: 0, y: 0, width: 10, height: 10, containerID: id, isEventCapture: cap });
  assert.throws(() => validatePage({ texts: [t(1, true), t(2, true)] }), EvenHubValidationError);
  assert.throws(() => validatePage({ texts: [t(1), t(1)] }), EvenHubValidationError);
  assert.throws(() => validatePage({}), EvenHubValidationError);
  assert.throws(() => validatePage({ images: [1, 2, 3, 4, 5].map((i) => t(i)) }), EvenHubValidationError);
  validatePage({ texts: [t(1, true)], menu: [{ itemName: 'a', itemID: 1 }] });
});

test('decode replies and device events', () => {
  const reply = new PbWriter().uint(1, 1).uint(2, 0x42).message(4, new PbWriter().uint(1, 0)).finish();
  assert.deepEqual(decodeMessage(reply), { type: 'result', cmd: 1, tag: 4, magic: 0x42, code: 0 });
  const ev = new PbWriter().uint(1, 2).message(13, new PbWriter().message(1,
    new PbWriter().uint(1, 4).string(2, 'menu').string(3, 'Two').uint(4, 1).uint(5, 3))).finish();
  assert.deepEqual(decodeMessage(ev), { type: 'event', cmd: 2, magic: 0, event: { kind: 'list', containerID: 4, containerName: 'menu', itemName: 'Two', itemIndex: 1, eventType: 3 } });
  const imu = new PbWriter().uint(1, 2).message(13, new PbWriter().message(3,
    new PbWriter().uint(1, 8).message(3, new PbWriter().fixed32f(1, 1.5).fixed32f(3, -2)))).finish();
  const d = decodeMessage(imu);
  assert.ok(d.type === 'event' && d.event.kind === 'sys');
  if (d.type === "event" && d.event.kind === "sys") assert.deepEqual(d.event.imu, { x: 1.5, y: 0, z: -2 });
});

test('bmp4 header matches firmware parser expectations', () => {
  const w = 21, h = 3; const g = Uint8Array.from({ length: w * h }, (_, i) => i * 4);
  const b = encodeBmp4(g, w, h); const dv = new DataView(b.buffer);
  assert.equal(String.fromCharCode(b[0], b[1]), 'BM');
  assert.equal(dv.getUint16(28, true), 4); assert.equal(dv.getInt32(18, true), w); assert.equal(dv.getUint32(10, true), 0x76);
  assert.equal(b.length, 0x76 + 12 * h); // stride ((21+1)/2+3)/4*4 = 12
  assert.equal(b[0x76 + 2 * 12] >> 4, g[0] >> 4); // bottom-up: top row stored last
});

test('rle and lz4 roundtrip; planner caps at w*h', () => {
  const w = 288, h = 144; const g = new Uint8Array(w * h); for (let i = 0; i < g.length; i++) g[i] = (i % w) < 144 ? 255 : (i * 7) & 0xff;
  const bmp = encodeBmp4(g, w, h);
  assert.deepEqual(rleDecode(rleEncode(bmp)), bmp);
  const lz = lz4BlockEncode(bmp); assert.deepEqual(lz4BlockDecode(lz, w * h), bmp);
  for (const n of [0, 1, 5, 13, 100]) { const s = Uint8Array.from({ length: n }, (_, i) => i & 3); assert.deepEqual(lz4BlockDecode(lz4BlockEncode(s), 1000), s); }
  const plan = planImage(bmp, w, h);
  assert.ok(plan.totalSize <= w * h && plan.compressMode === Compress.LZ4);
  assert.equal(plan.fragments.reduce((a, f) => a + f.length, 0), plan.totalSize);
  assert.ok(plan.fragments.every((f) => f.length <= 4000));
  for (const [k, f] of plan.fragments.entries()) assert.ok(encodeImageFragment({ containerID: 1, containerName: 'image-01', sessionId: 0xfffe, totalSize: plan.totalSize, compressMode: plan.compressMode, fragmentIndex: k, data: f }, 255).length <= 4096);
  assert.throws(() => planImage(new Uint8Array(500).map((_, i) => (i * 97) & 0xff), 20, 20, 'none'));
});

/** Loopback "glasses" that ACKs like the firmware: echoes magic, replies cmd+1/tag+1. */
function fakeGlasses(log: number[]): Link {
  let sink: (p: Uint8Array) => void = () => {};
  const rx = new Reassembler((m) => {
    const d = [...pbFields(m.payload)]; const cmd = (d.find((f) => f.tag === 1)?.value as number) ?? 0;
    const magic = d.find((f) => f.tag === 2)?.value as number; log.push(cmd);
    const body = cmd === 3 ? new PbWriter().uint(8, 4) : new PbWriter().uint(1, cmd === 0 ? 0 : cmd === 5 ? 8 : 0);
    const tag = cmd === 0 ? 4 : cmd === 3 ? 6 : cmd === 5 ? 10 : 99;
    const reply = new PbWriter().uint(1, cmd + 1).uint(2, magic).message(tag, body).finish();
    for (const p of encodeMessage({ serviceId: 0xe0, syncId: m.syncId, payload: reply, src: 2, dst: 1 })) queueMicrotask(() => sink(p));
  }, undefined, 0);
  return { mtu: 247, async write(p) { assert.equal(parseHeader(p).dst, 2); rx.push(p); }, onPacket(cb) { sink = cb; } };
}

test('client: request/reply by magic and serialized image stream', async () => {
  const log: number[] = []; const c = new EvenHubClient(fakeGlasses(log), { timeoutMs: 500 });
  await c.createPage({ images: [{ x: 0, y: 0, width: 288, height: 144, containerID: 1 }] });
  await c.updateText({ containerID: 1, content: 'x' });
  const g = Uint8Array.from({ length: 288 * 144 }, (_, i) => (i * 13) & 0xff);
  const bmp = encodeBmp4(g, 288, 144);
  await Promise.all([c.updateImage({ containerID: 1, width: 288, height: 144, bmp, compress: 'none' }),
                     c.updateImage({ containerID: 1, width: 288, height: 144, bmp, compress: 'none' })]);
  const frags = Math.ceil(bmp.length / 4000);
  assert.deepEqual(log, [0, 5, ...Array(frags * 2).fill(3)]);
  c.close();
});
