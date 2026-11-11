// Transport-agnostic EvenHub client: talks the firmware protocol directly over any
// byte link (Web Bluetooth, react-native-ble, noble, or the simulator).
import { encodeMessage, Reassembler, FLAG_SYNC } from './transport.ts';
import { EVENHUB_SERVICE_ID, Result, ImageStatus } from './schema.ts';
import {
  encodePage, encodeTextUpgrade, encodeImageFragment, encodeShutdown, encodeHeartbeat,
  encodeAudioControl, encodeImuControl, decodeMessage,
  type Page, type TextUpgrade, type Decoded, type DeviceEvent,
} from './messages.ts';
import { planImage, type CompressChoice } from './image.ts';

export interface Link {
  /** ATT MTU negotiated with the glasses (>= 247 on stock firmware). */
  readonly mtu: number;
  write(packet: Uint8Array): Promise<void>;
  /** Register a sink for notification packets. */
  onPacket(cb: (packet: Uint8Array) => void): void;
  /** Shared TPL sync-id allocator when several services multiplex one link. */
  nextSyncId?(): number;
}

export type ClientOptions = {
  serviceId?: number; flags?: number; timeoutMs?: number;
  /** Device schema line; '2.2' rejects 2.3-only fields (menu). */
  firmware?: '2.2' | '2.3';
  /**
   * rebuild/text/heartbeat/audio: resolve instead of throwing when no reply arrives.
   * Their success replies are sent later by the UI thread (evenhub_ui_page.c), not the
   * parser, and heartbeat/audio get none while the EvenHub app isn't running. Default true.
   */
  softAcks?: boolean;
  onWarning?: (msg: string) => void;
  onEvent?: (e: DeviceEvent) => void; onMessage?: (m: Decoded) => void;
};

export class EvenHubError extends Error {
  readonly code?: number;
  constructor(msg: string, code?: number) { super(msg); this.code = code; }
}

type Pending = { resolve: (d: Decoded) => void; reject: (e: Error) => void; timer: ReturnType<typeof setTimeout> };

export class EvenHubClient {
  private seq = 0; private sync = 0;
  private pending = new Map<string, Pending>();
  private rx: Reassembler;
  private imageChain: Promise<unknown> = Promise.resolve();
  private sessionCounter = 0;
  readonly serviceId: number; private flags: number; private timeoutMs: number;

  private link: Link; private opts: ClientOptions;
  constructor(link: Link, opts: ClientOptions = {}) {
    this.link = link; this.opts = opts;
    this.serviceId = opts.serviceId ?? EVENHUB_SERVICE_ID;
    this.flags = opts.flags ?? FLAG_SYNC;
    this.timeoutMs = opts.timeoutMs ?? 3000;
    this.rx = new Reassembler((m) => { if (m.serviceId === this.serviceId && m.payload.length) this.dispatch(m.payload); });
    link.onPacket((p) => this.rx.push(p));
  }

  private dispatch(payload: Uint8Array): void {
    let d: Decoded; try { d = decodeMessage(payload); } catch { return; }
    this.opts.onMessage?.(d);
    if (d.type === 'event') { this.opts.onEvent?.(d.event); return; }
    const key = `${d.cmd}/${d.magic}`;
    const p = this.pending.get(key);
    if (p) { clearTimeout(p.timer); this.pending.delete(key); p.resolve(d); }
  }

  private async send(build: (magic: number) => Uint8Array, replyCmd: number | null): Promise<Decoded | undefined> {
    const magic = (this.seq = (this.seq + 1) & 0xff);
    const payload = build(magic);
    const wait = replyCmd === null ? undefined : new Promise<Decoded>((resolve, reject) => {
      const key = `${replyCmd}/${magic}`;
      this.pending.get(key)?.reject(new EvenHubError('superseded'));
      const timer = setTimeout(() => { this.pending.delete(key); reject(new EvenHubError(`timeout waiting for cmd ${replyCmd}`)); }, this.timeoutMs);
      this.pending.set(key, { resolve, reject, timer });
    });
    const syncId = this.link.nextSyncId ? this.link.nextSyncId() : (this.sync = (this.sync + 1) & 0xff);
    for (const pkt of encodeMessage({ serviceId: this.serviceId, syncId, payload, flags: this.flags }, this.link.mtu)) await this.link.write(pkt);
    return wait;
  }

  private static expect(d: Decoded | undefined, ok: number): void {
    if (d?.type === 'result' && d.code !== ok) throw new EvenHubError(`firmware returned ${d.code}`, d.code);
  }

  private gate(p: Page): void {
    if (this.opts.firmware === '2.2' && p.menu?.length) throw new EvenHubError('menu containers need firmware >= 2.3');
  }
  async createPage(p: Page): Promise<void> { this.gate(p); EvenHubClient.expect(await this.send((m) => encodePage(p, m), 1), Result.CREATE_SUCCESS); }
  private async soft(p: Promise<Decoded | undefined>, what: string): Promise<Decoded | undefined> {
    if (this.opts.softAcks === false) return p;
    try { return await p; } catch (e) {
      if (e instanceof EvenHubError && /^timeout/.test(e.message)) { this.opts.onWarning?.(`${what}: no reply (${e.message})`); return undefined; }
      throw e;
    }
  }
  async rebuildPage(p: Page): Promise<void> { this.gate(p); EvenHubClient.expect(await this.soft(this.send((m) => encodePage(p, m, true), 8), 'rebuildPage'), Result.REBUILD_SUCCESS); }
  async updateText(u: TextUpgrade): Promise<void> { EvenHubClient.expect(await this.soft(this.send((m) => encodeTextUpgrade(u, m), 6), 'updateText'), Result.TEXT_SUCCESS); }
  async shutdown(exitMode: 0 | 1 = 0): Promise<void> { EvenHubClient.expect(await this.send((m) => encodeShutdown(exitMode, m), 10), Result.SHUTDOWN_SUCCESS); }
  async heartbeat(v = 1): Promise<void> { await this.soft(this.send((m) => encodeHeartbeat(v, m), 0x0c), 'heartbeat'); }
  async audio(open: boolean): Promise<void> { EvenHubClient.expect(await this.soft(this.send((m) => encodeAudioControl(open, m), 0x10), 'audio'), Result.AUDIO_SUCCESS); }
  async imu(enable: boolean, reportFrq = 0): Promise<void> { await this.send((m) => encodeImuControl(enable, reportFrq, m), 0x14); }

  /**
   * Stream a pre-built 4-bpp BMP to an image container. Transfers are serialized
   * (the firmware keeps a single session per container and requires sequential
   * fragment indices); each fragment waits for its ACK before the next.
   */
  updateImage(img: { containerID: number; containerName?: string; width: number; height: number; bmp: Uint8Array; compress?: CompressChoice }): Promise<void> {
    const run = async () => {
      const plan = planImage(img.bmp, img.width, img.height, img.compress ?? 'auto');
      const sessionId = (this.sessionCounter = (this.sessionCounter % 0xfffe) + 1);
      for (let i = 0; i < plan.fragments.length; i++) {
        const d = await this.send((m) => encodeImageFragment({
          containerID: img.containerID, containerName: img.containerName, sessionId, totalSize: plan.totalSize,
          compressMode: plan.compressMode, fragmentIndex: i, data: plan.fragments[i],
        }, m), 4);
        if (d?.type === 'imageResult' && d.status !== ImageStatus.OK) throw new EvenHubError(`image fragment ${i} rejected`, d.status);
      }
    };
    const p = this.imageChain.then(run, run);
    this.imageChain = p.catch(() => {});
    return p;
  }

  close(): void {
    for (const p of this.pending.values()) { clearTimeout(p.timer); p.reject(new EvenHubError('closed')); }
    this.pending.clear(); this.rx.reset();
  }
}
