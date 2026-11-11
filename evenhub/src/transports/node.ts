// Node transport via the optional peer dependency @abandonware/noble.
import { G2Gatt, G2_NAME_PREFIX } from '../gatt.ts';
import type { Link } from '../client.ts';

const toBuf = (b: Uint8Array): Uint8Array => ((globalThis as { Buffer?: { from(b: Uint8Array): Uint8Array } }).Buffer?.from(b) ?? b);
const short = (u: string) => u.replace(/-/g, '').toLowerCase();

type NobleChar = { uuid: string; write(d: Uint8Array, withoutResponse: boolean, cb?: (e?: Error) => void): void; subscribe(cb: (e?: Error) => void): void; on(ev: 'data', cb: (d: Uint8Array) => void): void };
type NoblePeripheral = {
  advertisement: { localName?: string }; mtu?: number | null;
  connect(cb: (e?: Error) => void): void; disconnect(cb?: () => void): void;
  discoverSomeServicesAndCharacteristics(s: string[], c: string[], cb: (e: Error | undefined, s: unknown[], c: NobleChar[]) => void): void;
};
type Noble = {
  state: string; on(ev: string, cb: (x: never) => void): void; removeListener(ev: string, cb: (x: never) => void): void;
  startScanning(s: string[], dup: boolean, cb?: (e?: Error) => void): void; stopScanning(): void;
};

export type NodeLink = Link & { peripheral: NoblePeripheral; disconnect(): Promise<void> };

/**
 * Scan for a G2 arm and open EUS. `match` defaults to the first name starting with
 * "Even G2" (pass e.g. n => n.includes('_R_') for the right/master arm; the side
 * marker in the advert name is unverified).
 */
export async function connectNode(opts: { match?: (name: string) => boolean; scanTimeoutMs?: number; noble?: Noble } = {}): Promise<NodeLink> {
  const mod = 'noble';
  const noble: Noble = opts.noble ?? ((await import(`@abandonware/${mod}`).catch(() => {
    throw new Error('install @abandonware/noble to use the Node transport');
  })) as { default: Noble }).default;
  const match = opts.match ?? ((n: string) => n.startsWith(G2_NAME_PREFIX));
  if (noble.state !== 'poweredOn') await new Promise<void>((res) => { const h = (s: string) => { if (s === 'poweredOn') { noble.removeListener('stateChange', h as never); res(); } }; noble.on('stateChange', h as never); });
  const p = await new Promise<NoblePeripheral>((res, rej) => {
    const timer = setTimeout(() => { noble.stopScanning(); rej(new Error('G2 not found')); }, opts.scanTimeoutMs ?? 15000);
    const h = (per: NoblePeripheral) => { const n = per.advertisement.localName ?? ''; if (match(n)) { clearTimeout(timer); noble.removeListener('discover', h as never); noble.stopScanning(); res(per); } };
    noble.on('discover', h as never);
    noble.startScanning([], false);
  });
  await new Promise<void>((res, rej) => p.connect((e) => (e ? rej(e) : res())));
  const chars = await new Promise<NobleChar[]>((res, rej) => p.discoverSomeServicesAndCharacteristics(
    [short(G2Gatt.eus.service)], [short(G2Gatt.eus.write), short(G2Gatt.eus.notify)], (e, _s, c) => (e ? rej(e) : res(c))));
  const tx = chars.find((c) => c.uuid === short(G2Gatt.eus.write)); const rx = chars.find((c) => c.uuid === short(G2Gatt.eus.notify));
  if (!tx || !rx) throw new Error('EUS characteristics not found');
  const sinks: ((b: Uint8Array) => void)[] = [];
  rx.on('data', (d) => { const b = new Uint8Array(d); for (const s of sinks) s(b); });
  await new Promise<void>((res, rej) => rx.subscribe((e) => (e ? rej(e) : res())));
  return {
    peripheral: p,
    mtu: p.mtu ?? 247,
    write: (b) => new Promise((res, rej) => tx.write(toBuf(b), true, (e) => (e ? rej(e) : res()))),
    onPacket: (cb) => { sinks.push(cb); },
    disconnect: () => new Promise((res) => p.disconnect(() => res())),
  };
}
