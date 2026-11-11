// Device-config / pairing service 0x80 (nanopb descriptor 0x7766dc,
// dispatcher APP_PbRxDevCfgFrameDataProcess 0x4d83d8, 2.2.6.10).
import { PbWriter, pbFields, pbNum, type PbField } from './pb.ts';

export const DEVCFG_SERVICE_ID = 0x80;

export const DevCfgCmd = {
  SecAuth: { cmd: 0x04, tag: 3 },
  PipeRole: { cmd: 0x05, tag: 4 },
  RingConnectInfo: { cmd: 0x06, tag: 5 },
  BleParams: { cmd: 0x07, tag: 6 },
  Disconnect: { cmd: 0x08, tag: 7 },
  Unpair: { cmd: 0x09, tag: 8 },
  ErrorCode: { cmd: 0x0a, tag: 9 },
  FactoryRestore: { cmd: 0x0d, tag: 12 },
  Heartbeat: { cmd: 0x0e, tag: 13 },
  QuickRestart: { cmd: 0x0f, tag: 14 },
  TimeSync: { cmd: 0x80, tag: 128 },
  AudControl: { cmd: 0x81, tag: 129 },
} as const;

/** ErrorCode.code returned for an unknown command. */
export const DEVCFG_NOT_SUPPORT = 8;

const env = (c: { cmd: number; tag: number }, magic: number, body: PbWriter) =>
  new PbWriter().uint(1, c.cmd).uintAlways(2, magic & 0xff).message(c.tag, body).finish();

/** SecAuth {1 secAuth, 2 phoneType}. Captured app traffic sends {1:1, 2:4}. */
export const encodeSecAuth = (magic: number, phoneType = 4) =>
  env(DevCfgCmd.SecAuth, magic, new PbWriter().uintAlways(1, 1).uint(2, phoneType));

/** PipeRole {1 asCmdRole}. Captured app traffic sends 2 then 1. */
export const encodePipeRole = (magic: number, role: number) =>
  env(DevCfgCmd.PipeRole, magic, new PbWriter().uintAlways(1, role));

/**
 * TimeSync {1 utc u32, 2 tz int8 (unit unverified), 3 u8}. Firmware field 3 is a u8; the community
 * captures send int64(-24) there (10-byte varint). `compatTxid` reproduces those bytes.
 */
export function encodeTimeSync(magic: number, opts: { utc?: number; tz?: number; compatTxid?: boolean } = {}): Uint8Array {
  const utc = opts.utc ?? Math.floor(Date.now() / 1000);
  let b = new PbWriter().uintAlways(1, utc).finish();
  const tz = opts.tz ?? 0;
  if (tz > 0) b = Uint8Array.from([...b, 0x10, tz]);
  // negative int8 (nanopb int32 wire) = 10-byte sign-extended varint
  else if (tz < 0) b = Uint8Array.from([...b, 0x10, ((tz & 0x7f)) | 0x80, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x01]);
  if (opts.compatTxid) b = Uint8Array.from([...b, 0x18, 0xe8, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x01]);
  return new PbWriter().uint(1, DevCfgCmd.TimeSync.cmd).uintAlways(2, magic & 0xff).bytes(DevCfgCmd.TimeSync.tag, b, true).finish();
}

/** Heartbeat (cmd 0x0E, tag 13): handler 0x543378 re-arms a 30 s link timer. */
export const encodeDevHeartbeat = (magic: number) => env(DevCfgCmd.Heartbeat, magic, new PbWriter());

export type DevCfgMsg = { cmd: number; magic: number; tag: number; body: Map<number, number | Uint8Array> };

export function decodeDevCfg(payload: Uint8Array): DevCfgMsg {
  let cmd = 0, magic = 0, tag = 0; const body = new Map<number, number | Uint8Array>();
  for (const f of pbFields(payload)) {
    if (f.tag === 1) cmd = pbNum(f.value);
    else if (f.tag === 2) magic = pbNum(f.value);
    else if (f.wire === 2) { tag = f.tag; for (const g of pbFields(f.value as Uint8Array) as Iterable<PbField>) body.set(g.tag, g.value); }
  }
  return { cmd, magic, tag, body };
}
