// Setting service 0x09 (descriptor 0x77772c). Full-status request = oneof tag 4;
// setting_parse_data_package 0x49b1f8 drops duplicate 32-bit magics and records cmd/magic;
// setting_data_recv_handler 0x466976 answers kind 4 via setting_respond_with_local_data
// 0x49b7c4/0x49ba58 (right/master arm only, and only if cmd != 0);
// setting_build_full_status_package 0x49b4da fills tag5 = left version, tag6 = right version.
import { PbWriter, pbFields, pbNum, pbStr } from './pb.ts';

export const SETTING_SERVICE_ID = 0x09;
export const SettingF = { fullStatus: 4, leftVersion: 5, rightVersion: 6 } as const;

/** G2SettingPackage commandId (SybilSight G2SettingCommandId; firmware only checks != 0). */
export const SettingCmd = { DeviceReceiveInfo: 1, DeviceReceiveRequest: 2, DeviceSendToApp: 3, DeviceRespondToApp: 4 } as const;

/** Request {1:2, 2:magic, 4:{1 settingInfoType=1 APP_REQUIRE_BASIC_SETTING}} (as sent by the stock app / SybilSight). */
export const encodeStatusRequest = (magic: number) =>
  new PbWriter().uintAlways(1, SettingCmd.DeviceReceiveRequest).uintAlways(2, magic >>> 0)
    .message(SettingF.fullStatus, new PbWriter().uintAlways(1, 1)).finish();

/**
 * Settings writes: {1:1, 2:magic, 3: DeviceReceiveInfoFromAPP{<oneof n>: {...}}}.
 * Firmware: kind 3 -> setting_handle_device_receive_info 0x466abc switches on the inner
 * oneof tag (1..12), then setting_respond_to_app 0x49b900 replies {1:1, 2:echoed magic}.
 * Inner layouts from SybilSight G2.swift (hardware-tested there). Always send every field
 * of an inner message: an omitted proto3 field is applied as 0, not "unchanged".
 */
export const SettingWriteF = { brightness: 1, yCoordinate: 2, xCoordinate: 3, headUp: 4, silentMode: 6 } as const;
export type SettingWrite =
  | { kind: 'brightnessAuto'; enabled: boolean }               // {1 type=1, 2 value}
  | { kind: 'brightnessLevel'; level: number }                 // {1 type=2, 2 value}
  | { kind: 'brightnessCalibration'; left: number; right: number } // {3 left, 4 right} 0..10
  | { kind: 'screenHeight'; level: number }                    // Y 0..12
  | { kind: 'screenDepth'; level: number }                     // X 0..2
  | { kind: 'headUp'; enabled: boolean; angle: number }        // {1 switch, 2 angle 0..60}
  | { kind: 'silentMode'; enabled: boolean };

export function encodeSettingWrite(magic: number, w: SettingWrite): Uint8Array {
  let tag: number; const b = new PbWriter();
  switch (w.kind) {
    case 'brightnessAuto': tag = SettingWriteF.brightness; b.uintAlways(1, 1).uintAlways(2, w.enabled ? 1 : 0); break;
    case 'brightnessLevel': tag = SettingWriteF.brightness; b.uintAlways(1, 2).uintAlways(2, w.level); break;
    case 'brightnessCalibration': tag = SettingWriteF.brightness; b.uintAlways(3, w.left).uintAlways(4, w.right); break;
    case 'screenHeight': tag = SettingWriteF.yCoordinate; b.uintAlways(1, w.level); break;
    case 'screenDepth': tag = SettingWriteF.xCoordinate; b.uintAlways(1, w.level); break;
    case 'headUp': tag = SettingWriteF.headUp; b.uintAlways(1, w.enabled ? 1 : 0).uintAlways(2, w.angle); break;
    case 'silentMode': tag = SettingWriteF.silentMode; b.uintAlways(1, w.enabled ? 1 : 0); break;
  }
  return new PbWriter().uintAlways(1, SettingCmd.DeviceReceiveInfo).uintAlways(2, magic >>> 0)
    .message(3, new PbWriter().message(tag, b)).finish();
}

/** Root cmd + magic of any setting-service message (used to match write acks). */
export function decodeSettingHeader(payload: Uint8Array): { cmd: number; magic: number } {
  let cmd = 0, magic = 0;
  for (const f of pbFields(payload)) { if (f.tag === 1) cmd = pbNum(f.value); else if (f.tag === 2) magic = pbNum(f.value); }
  return { cmd, magic };
}

export type StatusReply = { cmd: number; magic: number; leftVersion: string; rightVersion: string; fields: Map<number, number | Uint8Array> };

export function decodeStatus(payload: Uint8Array): StatusReply | undefined {
  let cmd = 0, magic = 0, sub: Uint8Array | undefined;
  for (const f of pbFields(payload)) {
    if (f.tag === 1) cmd = pbNum(f.value);
    else if (f.tag === 2) magic = pbNum(f.value);
    else if (f.tag === SettingF.fullStatus && f.wire === 2) sub = f.value as Uint8Array;
  }
  if (!sub) return undefined;
  const fields = new Map<number, number | Uint8Array>();
  for (const g of pbFields(sub)) fields.set(g.tag, g.value);
  const s = (t: number) => (fields.has(t) ? pbStr(fields.get(t)!) : '');
  return { cmd, magic, leftVersion: s(SettingF.leftVersion), rightVersion: s(SettingF.rightVersion), fields };
}

export type FirmwareLine = '2.2' | '2.3';
/** Map "2.2.6.10" / "2.3.2.14" to a schema line; anything >= 2.3 uses the 2.3 schema. */
export function firmwareLine(version: string): FirmwareLine | undefined {
  const m = /^(\d+)\.(\d+)/.exec(version.trim());
  if (!m) return undefined;
  const maj = +m[1], min = +m[2];
  if (maj < 2 || (maj === 2 && min < 2)) return undefined;
  return maj === 2 && min === 2 ? '2.2' : '2.3';
}
