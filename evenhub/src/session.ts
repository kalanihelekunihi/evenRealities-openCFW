// One BLE link to the master (right) arm, multiplexing TPL services, plus the
// stock-app connect handshake reconstructed from firmware (see docs/DESIGN.md §6).
import { encodeMessage, Reassembler, FLAG_SYNC } from './transport.ts';
import type { Link } from './client.ts';
import { EvenHubClient, EvenHubError, type ClientOptions } from './client.ts';
import {
  DEVCFG_SERVICE_ID, DevCfgCmd, encodeSecAuth, encodePipeRole, encodeTimeSync, encodeDevHeartbeat, decodeDevCfg, type DevCfgMsg,
} from './devcfg.ts';
import { SETTING_SERVICE_ID, encodeSettingWrite, decodeSettingHeader, type SettingWrite, encodeStatusRequest, decodeStatus, firmwareLine, type FirmwareLine, type StatusReply } from './setting.ts';

type Listener = (serviceId: number, payload: Uint8Array) => void;

export class Session {
  readonly link: Link;
  private sync = 0;
  private listeners = new Set<Listener>();
  private raw = new Set<(p: Uint8Array) => void>();
  private rx: Reassembler;
  constructor(link: Link) {
    this.link = link;
    this.rx = new Reassembler((m) => { for (const l of this.listeners) l(m.serviceId, m.payload); });
    link.onPacket((p) => { this.rx.push(p); for (const r of this.raw) r(p); });
  }
  nextSyncId(): number { return (this.sync = (this.sync + 1) & 0xff); }
  /** A Link view for EvenHubClient sharing this session's sync ids. */
  asLink(): Link {
    return { mtu: this.link.mtu, write: (p) => this.link.write(p), onPacket: (cb) => { this.raw.add(cb); }, nextSyncId: () => this.nextSyncId() };
  }
  on(l: Listener): () => void { this.listeners.add(l); return () => this.listeners.delete(l); }
  async send(serviceId: number, payload: Uint8Array, flags = FLAG_SYNC): Promise<void> {
    for (const p of encodeMessage({ serviceId, syncId: this.nextSyncId(), payload, flags }, this.link.mtu)) await this.link.write(p);
  }
  /** Send and wait for the first message on `serviceId` accepted by `match`. */
  request<T>(serviceId: number, payload: Uint8Array, match: (p: Uint8Array) => T | undefined, timeoutMs: number, flags = FLAG_SYNC): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const off = this.on((svc, p) => {
        if (svc !== serviceId) return;
        let r: T | undefined; try { r = match(p); } catch { return; }
        if (r !== undefined) { clearTimeout(timer); off(); resolve(r); }
      });
      const timer = setTimeout(() => { off(); reject(new EvenHubError(`timeout on service 0x${serviceId.toString(16)}`)); }, timeoutMs);
      this.send(serviceId, payload, flags).catch((e) => { clearTimeout(timer); off(); reject(e); });
    });
  }
}

export type ConnectOptions = {
  /** devcfg SecAuth.phoneType; captures show 4. */
  phoneType?: number;
  /** PipeRole values sent in order; captures show [2, 1] (full) or [2] (fast). */
  pipeRoles?: number[];
  /** Reproduce the captured 10-byte TimeSync field 3 (-24). Default true (matches working captures). */
  compatTxid?: boolean;
  tz?: number;
  timeoutMs?: number;
  /** Fail connect if no SecAuth reply arrives (default false: captures don't wait). */
  requireAuthReply?: boolean;
  /** devcfg heartbeat period, must stay under the firmware's 30 s window. 0 disables. */
  heartbeatMs?: number;
  /** Override detection (e.g. from advertising data). */
  firmware?: FirmwareLine;
  client?: ClientOptions;
  log?: (msg: string) => void;
};

export type Connection = {
  session: Session; hub: EvenHubClient; firmware: FirmwareLine;
  versions: { left: string; right: string } | undefined;
  authReply: DevCfgMsg | undefined;
  /** Write one glasses setting (service 0x09); resolves when the magic-echo ack arrives. */
  writeSetting(w: SettingWrite): Promise<void>;
  close(): void;
};

/** GATT-level steps (MTU, EUS discovery, CCC enable, Just Works bonding) are the transport's job. */
export async function connect(link: Link, opts: ConnectOptions = {}): Promise<Connection> {
  const s = new Session(link);
  const t = opts.timeoutMs ?? 3000;
  const log = opts.log ?? (() => {});
  let magic = Math.floor(Math.random() * 256);
  const next = () => (magic = (magic + 1) & 0xff);

  // 1. SecAuth (cmd 4). Immediate reply echoes the magic (PB_TxEncodeSecAuth 0x4bb576);
  //    the post-encryption NotifySecAuth (0x4bb92c) carries a tick-count magic, so accept any cmd 4.
  let authReply: DevCfgMsg | undefined;
  try {
    authReply = await s.request(DEVCFG_SERVICE_ID, encodeSecAuth(next(), opts.phoneType ?? 4), (p) => {
      const d = decodeDevCfg(p); return d.cmd === DevCfgCmd.SecAuth.cmd ? d : undefined;
    }, t, 0x00);
  } catch (e) { if (opts.requireAuthReply) throw e; log('no SecAuth reply; continuing'); }

  // 2. PipeRole (cmd 5), 3. TimeSync (cmd 0x80): replies echo the request magic.
  const echo = (cmd: number, m: number) => (p: Uint8Array) => { const d = decodeDevCfg(p); return d.cmd === cmd && d.magic === m ? d : undefined; };
  const soft = async (cmd: number, payload: (m: number) => Uint8Array) => {
    const m = next();
    try { await s.request(DEVCFG_SERVICE_ID, payload(m), echo(cmd, m), t); } catch { log(`no reply to devcfg cmd 0x${cmd.toString(16)}`); }
  };
  for (const role of opts.pipeRoles ?? [2]) await soft(DevCfgCmd.PipeRole.cmd, (m) => encodePipeRole(m, role));
  await soft(DevCfgCmd.TimeSync.cmd, (m) => encodeTimeSync(m, { compatTxid: opts.compatTxid ?? true, tz: opts.tz }));

  // 4. Version: setting full status (tag 4). Left version may be empty on the first ask
  //    (firmware requests it from the slave arm), so retry once.
  let versions: Connection['versions'];
  let firmware = opts.firmware;
  if (!firmware) {
    for (let i = 0; i < 2 && !(versions?.left && versions.right); i++) {
      const m = (Math.random() * 0xffffffff) >>> 0;
      try {
        const r: StatusReply = await s.request(SETTING_SERVICE_ID, encodeStatusRequest(m), (p) => {
          const d = decodeStatus(p); return d && d.magic === m ? d : undefined;
        }, t);
        versions = { left: r.leftVersion, right: r.rightVersion };
      } catch { log('no setting status reply'); break; }
      if (!versions.left) await new Promise((r) => setTimeout(r, 300));
    }
    firmware = firmwareLine(versions?.right ?? '') ?? firmwareLine(versions?.left ?? '');
    if (!firmware) throw new EvenHubError(`cannot determine firmware version (${JSON.stringify(versions)}); pass opts.firmware`);
  }

  // 5. Keepalive (devcfg cmd 0x0E; handler 0x543378 re-arms a 30 s timer).
  const hbMs = opts.heartbeatMs ?? 15000;
  const hb = hbMs > 0 ? setInterval(() => { s.send(DEVCFG_SERVICE_ID, encodeDevHeartbeat(next())).catch(() => {}); }, hbMs) : undefined;
  (hb as { unref?: () => void } | undefined)?.unref?.();

  const hub = new EvenHubClient(s.asLink(), { ...opts.client, firmware });
  const writeSetting = async (w: SettingWrite) => {
    const m = (Math.random() * 0xffffffff) >>> 0;
    await s.request(SETTING_SERVICE_ID, encodeSettingWrite(m, w), (p) => (decodeSettingHeader(p).magic === m ? true : undefined), t);
  };
  return { session: s, hub, firmware, versions, authReply, writeSetting, close() { if (hb) clearInterval(hb); hub.close(); } };
}
