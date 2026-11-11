// Web Bluetooth transport (Chrome/Edge/Bluefy). Bonding: the glasses send an SMP
// security request (APP_SlaveStartSecurityRequestEvent 0x46effc); smpCfg 0x774D44 is
// NoInputNoOutput + bonding, no MITM, so the OS performs "Just Works" pairing itself.
import { G2Gatt, G2_NAME_PREFIX } from '../gatt.ts';
import type { Link } from '../client.ts';

// Minimal structural types so the SDK compiles without the DOM lib.
type Char = {
  writeValueWithoutResponse(v: Uint8Array): Promise<void>;
  startNotifications(): Promise<unknown>;
  addEventListener(t: 'characteristicvaluechanged', cb: (e: { target: { value: DataView } }) => void): void;
};
type Device = {
  name?: string;
  gatt: { connect(): Promise<{ getPrimaryService(u: string): Promise<{ getCharacteristic(u: string): Promise<Char> }>; disconnect(): void }> };
  addEventListener(t: 'gattserverdisconnected', cb: () => void): void;
};

export type WebBluetoothLink = Link & { device: Device; disconnect(): void };

export async function requestG2(opts: { namePrefix?: string; mtu?: number; device?: Device; onDisconnect?: () => void } = {}): Promise<WebBluetoothLink> {
  const bt = (globalThis as { navigator?: { bluetooth?: { requestDevice(o: unknown): Promise<Device> } } }).navigator?.bluetooth;
  if (!opts.device && !bt) throw new Error('Web Bluetooth not available');
  const device = opts.device ?? await bt!.requestDevice({
    filters: [{ namePrefix: opts.namePrefix ?? G2_NAME_PREFIX }],
    optionalServices: [G2Gatt.eus.service],
  });
  const server = await device.gatt.connect();
  const svc = await server.getPrimaryService(G2Gatt.eus.service);
  const tx = await svc.getCharacteristic(G2Gatt.eus.write);
  const rx = await svc.getCharacteristic(G2Gatt.eus.notify);
  const sinks: ((p: Uint8Array) => void)[] = [];
  rx.addEventListener('characteristicvaluechanged', (e) => {
    const v = e.target.value; const p = new Uint8Array(v.buffer.slice(v.byteOffset, v.byteOffset + v.byteLength));
    for (const s of sinks) s(p);
  });
  await rx.startNotifications(); // writes 01 00 to the 5402 CCC
  if (opts.onDisconnect) device.addEventListener('gattserverdisconnected', opts.onDisconnect);
  return {
    device,
    // Web Bluetooth hides the ATT MTU; stock firmware negotiates >= 247.
    mtu: opts.mtu ?? 247,
    write: (p) => tx.writeValueWithoutResponse(p),
    onPacket: (cb) => { sinks.push(cb); },
    disconnect: () => server.disconnect(),
  };
}
