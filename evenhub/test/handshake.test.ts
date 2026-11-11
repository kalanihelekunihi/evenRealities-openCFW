import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  encodeMessage, Reassembler, PbWriter, pbFields, pbNum, connect, decodeDevCfg, encodeSecAuth, encodeTimeSync,
  encodeStatusRequest, decodeStatus, encodeSettingWrite, EvenHubClient, EvenHubValidationError, encodePage, firmwareLine, G2Gatt, requestG2, EvenHubError,
  DEVCFG_SERVICE_ID, SETTING_SERVICE_ID, type Link,
} from '../src/index.ts';

const hex = (b: Uint8Array) => Buffer.from(b).toString('hex');

type FakeOpts = { encrypted?: boolean; left?: string; right?: string; silentSetting?: boolean; leftLate?: boolean };
/** Models the right (master) arm: devcfg 0x80, setting 0x09, EvenHub 0xE0. */
function fakeArm(o: FakeOpts = {}) {
  let sink: (p: Uint8Array) => void = () => {};
  const seen: { svc: number; cmd: number; flags: number }[] = [];
  let encrypted = o.encrypted ?? true; let lastSettingMagic = -1; let leftAsked = 0;
  const reply = (svc: number, payload: Uint8Array) => {
    for (const p of encodeMessage({ serviceId: svc, syncId: 0, payload, src: 2, dst: 1 })) queueMicrotask(() => sink(p));
  };
  const notifySecAuth = () => reply(0x80, new PbWriter().uint(1, 4).uintAlways(2, 0x37 /* tick */).message(3, new PbWriter().uint(1, 1)).finish());
  const rx = new Reassembler((m) => {
    const f = new Map([...pbFields(m.payload)].map((x) => [x.tag, x.value]));
    const cmd = pbNum(f.get(1) ?? 0), magic = pbNum(f.get(2) ?? 0);
    seen.push({ svc: m.serviceId, cmd, flags: m.flags });
    if (m.serviceId === 0x80) {
      if (cmd === 4) {
        reply(0x80, new PbWriter().uint(1, 4).uintAlways(2, magic).message(3, new PbWriter().uint(1, 1)).finish());
        if (encrypted) setTimeout(notifySecAuth, 5);
      } else if (cmd === 5 || cmd === 0x80) {
        reply(0x80, new PbWriter().uint(1, cmd).uintAlways(2, magic).message(cmd === 5 ? 4 : 128, new PbWriter().uint(1, 1)).finish());
      } else if (cmd === 0x0e) { /* heartbeat: no reply */ }
      else reply(0x80, new PbWriter().uint(1, 10).uintAlways(2, magic).message(9, new PbWriter().uint(1, cmd).uint(2, 8)).finish());
    } else if (m.serviceId === 0x09) {
      if (o.silentSetting || magic === lastSettingMagic || !cmd) return;
      if (cmd === 1) { lastSettingMagic = magic; reply(0x09, new PbWriter().uint(1, 1).uintAlways(2, magic).finish()); return; } // duplicate filter 0x49b198, cmd==0 => no reply
      lastSettingMagic = magic;
      const left = o.leftLate && leftAsked++ === 0 ? '' : (o.left ?? '2.2.6.10');
      const st = new PbWriter().uint(2, 80).string(5, left).string(6, o.right ?? '2.2.6.10');
      reply(0x09, new PbWriter().uint(1, 2).uintAlways(2, magic).message(4, st).finish());
    } else if (m.serviceId === 0xe0) {
      reply(0xe0, new PbWriter().uint(1, cmd + 1).uint(2, magic).message(4, new PbWriter().uint(1, 0)).finish());
    }
  }, undefined, 0);
  const link: Link = { mtu: 247, async write(p) { rx.push(p); }, onPacket(cb) { sink = cb; } };
  return { link, seen, encrypt() { encrypted = true; notifySecAuth(); } };
}

test('devcfg encoders match captured app bytes', () => {
  assert.equal(hex(encodeSecAuth(0x0d)), '0804' + '100d' + '1a04' + '08011004');
  const ts = encodeTimeSync(0x0f, { utc: 1700000000, compatTxid: true }); // block length 0x11 as in captures
  assert.equal(hex(ts), '088001' + '100f' + '820811' + '0880e2cfaa06' + '18e8ffffffffffffffff01');
  assert.ok(hex(encodeTimeSync(1, { utc: 1, tz: -8 })).endsWith('0801' + '10f8ffffffffffffffff01'));
  const d = decodeDevCfg(encodeSecAuth(9, 3));
  assert.deepEqual([d.cmd, d.magic, d.tag, d.body.get(2)], [4, 9, 3, 3]);
});

test('setting status request/decode and version line', () => {
  assert.equal(hex(encodeStatusRequest(5)), '0802' + '1005' + '22020801');
  const r = decodeStatus(new PbWriter().uint(1, 2).uint(2, 5).message(4, new PbWriter().string(5, '2.3.2.14').string(6, '2.3.2.14')).finish())!;
  assert.equal(r.rightVersion, '2.3.2.14');
  assert.equal(firmwareLine('2.2.6.10'), '2.2'); assert.equal(firmwareLine('2.3.2.14'), '2.3'); assert.equal(firmwareLine('2.4.0'), '2.3');
  assert.equal(firmwareLine(''), undefined); assert.equal(firmwareLine('1.9'), undefined);
});

test('connect: full handshake order, flags, version detect 2.2, menu gated', async () => {
  const arm = fakeArm();
  const c = await connect(arm.link, { heartbeatMs: 0, timeoutMs: 200 });
  assert.equal(c.firmware, '2.2'); assert.deepEqual(c.versions, { left: '2.2.6.10', right: '2.2.6.10' });
  assert.equal(c.authReply?.cmd, 4);
  assert.deepEqual(arm.seen.map((s) => [s.svc, s.cmd]), [[0x80, 4], [0x80, 5], [0x80, 0x80], [0x09, 2]]);
  assert.equal(arm.seen[0].flags, 0x00); assert.equal(arm.seen[1].flags, 0x20);
  await c.hub.createPage({ texts: [{ x: 0, y: 0, width: 10, height: 10, containerID: 1, content: 'a' }] });
  await assert.rejects(c.hub.createPage({ texts: [{ x: 0, y: 0, width: 10, height: 10, containerID: 1 }], menu: [{ itemName: 'x', itemID: 1 }] }), EvenHubError);
  c.close();
});

test('connect: 2.3 device, late left version retried', async () => {
  const arm = fakeArm({ left: '2.3.2.14', right: '2.3.2.14', leftLate: true });
  const c = await connect(arm.link, { heartbeatMs: 0, timeoutMs: 200 });
  assert.equal(c.firmware, '2.3'); assert.equal(c.versions?.left, '2.3.2.14');
  assert.equal(arm.seen.filter((s) => s.svc === 0x09).length, 2);
  c.close();
});

test('connect: unencrypted link still gets the echo reply; version override; failure without version', async () => {
  const arm = fakeArm({ encrypted: false, silentSetting: true });
  await assert.rejects(connect(arm.link, { heartbeatMs: 0, timeoutMs: 50 }), /firmware version/);
  const c = await connect(fakeArm({ silentSetting: true }).link, { heartbeatMs: 0, timeoutMs: 50, firmware: '2.3' });
  assert.equal(c.firmware, '2.3'); c.close();
});

test('connect: heartbeat runs on devcfg 0x0E', async () => {
  const arm = fakeArm();
  const c = await connect(arm.link, { heartbeatMs: 10, timeoutMs: 200 });
  await new Promise((r) => setTimeout(r, 45)); c.close();
  assert.ok(arm.seen.filter((s) => s.svc === DEVCFG_SERVICE_ID && s.cmd === 0x0e).length >= 2);
  assert.equal(SETTING_SERVICE_ID, 9);
});

test('web bluetooth transport wires EUS 5401/5402', async () => {
  const writes: Uint8Array[] = []; let listener: ((e: { target: { value: DataView } }) => void) | undefined; let started = false;
  const asked: string[] = [];
  const char = (u: string) => ({
    uuid: u,
    async writeValueWithoutResponse(v: Uint8Array) { assert.equal(u, G2Gatt.eus.write); writes.push(v); },
    async startNotifications() { assert.equal(u, G2Gatt.eus.notify); started = true; },
    addEventListener(_t: string, cb: typeof listener) { listener = cb; },
  });
  const device = {
    name: 'Even G2_00_R_A', addEventListener() {},
    gatt: { async connect() { return { disconnect() {}, async getPrimaryService(s: string) { asked.push(s); return { async getCharacteristic(u: string) { return char(u); } }; } }; } },
  };
  const link = await requestG2({ device });
  assert.deepEqual(asked, [G2Gatt.eus.service]); assert.ok(started);
  assert.equal(G2Gatt.eus.service, '00002760-08c2-11e1-9073-0e8ac72e5450');
  let got: Uint8Array | undefined; link.onPacket((p) => (got = p));
  listener!({ target: { value: new DataView(Uint8Array.of(1, 2, 3).buffer) } });
  assert.deepEqual([...got!], [1, 2, 3]);
  await link.write(Uint8Array.of(9)); assert.equal(writes.length, 1);
});

test('settings writes: formats from SybilSight, magic-echo ack', async () => {
  assert.equal(hex(encodeSettingWrite(7, { kind: 'brightnessLevel', level: 40 })), '0801' + '1007' + '1a06' + '0a04' + '08021028');
  assert.equal(hex(encodeSettingWrite(7, { kind: 'headUp', enabled: false, angle: 20 })), '080110071a06' + '2204' + '08001014');
  assert.equal(hex(encodeSettingWrite(7, { kind: 'silentMode', enabled: false })), '080110071a04' + '32020800');
  const arm = fakeArm();
  const c = await connect(arm.link, { heartbeatMs: 0, timeoutMs: 200 });
  await c.writeSetting({ kind: 'screenHeight', level: 6 });
  assert.deepEqual(arm.seen.at(-1), { svc: 9, cmd: 1, flags: 0x20 });
  c.close();
});

test('page validation: zOrder all-or-nothing/unique, ranges, canvas', () => {
  const t = (o: object) => ({ x: 0, y: 0, width: 10, height: 10, containerID: 1, ...o });
  assert.throws(() => encodePage({ texts: [t({ zOrderIndex: 0 }), t({ containerID: 2 })] }, 1), EvenHubValidationError);
  assert.throws(() => encodePage({ texts: [t({ zOrderIndex: 1 }), t({ containerID: 2, zOrderIndex: 1 })] }, 1), EvenHubValidationError);
  assert.throws(() => encodePage({ texts: [t({ borderWidth: 6 })] }, 1), EvenHubValidationError);
  assert.throws(() => encodePage({ texts: [t({ x: 570 })] }, 1), EvenHubValidationError);
  // zOrderIndex 0 is emitted explicitly (tag 13)
  assert.ok(hex(encodePage({ texts: [t({ zOrderIndex: 0 })] }, 1)).includes('6800'));
});

test('soft acks: rebuild/text without reply resolve with a warning; strict mode throws', async () => {
  const silent: Link = { mtu: 247, async write() {}, onPacket() {} };
  const warns: string[] = [];
  const c = new EvenHubClient(silent, { timeoutMs: 20, onWarning: (w) => warns.push(w) });
  await c.updateText({ containerID: 1, content: 'x' });
  await c.rebuildPage({ texts: [{ x: 0, y: 0, width: 10, height: 10, containerID: 1 }] });
  assert.equal(warns.length, 2);
  const strict = new EvenHubClient(silent, { timeoutMs: 20, softAcks: false });
  await assert.rejects(strict.updateText({ containerID: 1, content: 'x' }), EvenHubError);
});
