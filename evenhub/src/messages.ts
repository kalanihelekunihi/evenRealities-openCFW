// EvenHub message encode/decode against the firmware schema (src/schema.ts).
import { PbWriter, pbFields, pbStr, pbF32, pbNum, utf8 } from './pb.ts';
import {
  Cmd, ROOT, CreateF, RebuildF, ListF, ListItemsF, TextF, ImageF, MenuF, MenuItemF, ImgRawF,
  TextUpgradeF, DeviceEventF, ListEventF, TextEventF, SysEventF, Limits, Display,
} from './schema.ts';

export type Box = {
  x: number; y: number; width: number; height: number;
  containerID: number; containerName?: string; zOrderIndex?: number;
};
export type Border = { borderWidth?: number; borderColor?: number; borderRadius?: number; padding?: number };
export type ListContainer = Box & Border & {
  items: string[]; itemWidth?: number; selectBorder?: boolean; isEventCapture?: boolean;
};
export type TextContainer = Box & Border & { content?: string; isEventCapture?: boolean; textColor?: number };
export type ImageContainer = Box;
export type MenuItem = { itemName: string; itemID: number };
export type Page = {
  lists?: ListContainer[]; texts?: TextContainer[]; images?: ImageContainer[];
  menu?: MenuItem[]; widgetId?: number;
};

export class EvenHubValidationError extends Error {}

const byteLen = (s: string | undefined) => (s ? utf8.encode(s).length : 0);
function check(cond: boolean, msg: string): void { if (!cond) throw new EvenHubValidationError(msg); }

/** Validate against the firmware's static storage and dispatcher rules (not the SDK's prose limits). */
export function validatePage(p: Page): void {
  const lists = p.lists ?? [], texts = p.texts ?? [], images = p.images ?? [];
  check(lists.length <= Limits.maxListContainers, `at most ${Limits.maxListContainers} list containers`);
  check(texts.length <= Limits.maxTextContainers, `at most ${Limits.maxTextContainers} text containers`);
  check(images.length <= Limits.maxImageContainers, `at most ${Limits.maxImageContainers} image containers`);
  const all: Box[] = [...lists, ...texts, ...images];
  check(all.length >= 1 && all.length <= Limits.maxObjects, 'page needs 1..12 containers');
  const ids = new Set<number>();
  for (const b of all) {
    check(!ids.has(b.containerID), `duplicate containerID ${b.containerID}`); ids.add(b.containerID);
    check(byteLen(b.containerName) <= Limits.containerNameBytes, `containerName > ${Limits.containerNameBytes} bytes`);
  }
  for (const b of all) {
    check(b.x >= 0 && b.y >= 0 && b.width >= 0 && b.height >= 0 && b.x + b.width <= Display.width && b.y + b.height <= Display.height,
      `container ${b.containerID} outside ${Display.width}x${Display.height}`);
  }
  for (const b of [...lists, ...texts] as (Box & Border)[]) {
    check((b.borderWidth ?? 0) >= 0 && (b.borderWidth ?? 0) <= Limits.borderWidth, 'borderWidth 0..5');
    check((b.borderColor ?? 0) >= 0 && (b.borderColor ?? 0) <= Limits.borderColor, 'borderColor 0..15');
    check((b.borderRadius ?? 0) >= 0 && (b.borderRadius ?? 0) <= Limits.borderRadius, 'borderRadius 0..10');
    check((b.padding ?? 0) >= 0 && (b.padding ?? 0) <= Limits.padding, 'padding 0..32');
  }
  // zOrderIndex (SDK 0.0.12): all-or-nothing per page, unique, larger = front.
  const z = (all as { zOrderIndex?: number }[]).map((b) => b.zOrderIndex);
  const zSet = z.filter((v) => v !== undefined);
  check(zSet.length === 0 || zSet.length === z.length, 'zOrderIndex must be set on every container or none');
  check(new Set(zSet).size === zSet.length, 'zOrderIndex values must be unique');
  check(zSet.every((v) => Number.isInteger(v) && v! >= 0), 'zOrderIndex must be a non-negative integer');
  const captures = lists.filter((l) => l.isEventCapture).length + texts.filter((t) => t.isEventCapture).length;
  check(captures <= Limits.maxEventCapture, 'only one container may capture events');
  for (const l of lists) {
    check(l.items.length >= 1 && l.items.length <= Limits.listItems, `list needs 1..${Limits.listItems} items`);
    for (const it of l.items) check(byteLen(it) <= Limits.listItemNameBytes, 'list item name too long');
  }
  for (const t of texts) {
    check(byteLen(t.content) <= Limits.textCreateBytes, `text content > ${Limits.textCreateBytes} bytes at create`);
    check(t.textColor === undefined || (t.textColor >= 0 && t.textColor <= 4), 'textColor must be 0..4');
  }
  if (p.menu) {
    check(p.menu.length <= Limits.menuItems, `at most ${Limits.menuItems} menu items`);
    const mids = new Set<number>();
    for (const m of p.menu) {
      check(m.itemID > 0 && !mids.has(m.itemID), 'menu itemID must be unique and non-zero'); mids.add(m.itemID);
      check(byteLen(m.itemName) <= Limits.menuNameBytes, 'menu itemName too long');
    }
  }
}

function boxCommon(w: PbWriter, b: Box & Border, F: typeof ListF | typeof TextF): void {
  w.uint(F.x, b.x).uint(F.y, b.y).uint(F.width, b.width).uint(F.height, b.height)
    .uint(F.borderWidth, b.borderWidth).uint(F.borderColor, b.borderColor)
    .uint(F.borderRadius, b.borderRadius).uint(F.padding, b.padding)
    .uint(F.containerID, b.containerID).string(F.containerName, b.containerName);
}

function encList(l: ListContainer): PbWriter {
  const w = new PbWriter(); boxCommon(w, l, ListF);
  const items = new PbWriter().uint(ListItemsF.itemCount, l.items.length).uint(ListItemsF.itemWidth, l.itemWidth)
    .uint(ListItemsF.isItemSelectBorderEn, l.selectBorder ? 1 : 0);
  for (const s of l.items) items.bytes(ListItemsF.itemName, utf8.encode(s), true);
  w.message(ListF.itemContainer, items).uint(ListF.isEventCapture, l.isEventCapture ? 1 : 0).opt(ListF.zOrderIndex, l.zOrderIndex);
  return w;
}
function encText(t: TextContainer): PbWriter {
  const w = new PbWriter(); boxCommon(w, t, TextF);
  return w.uint(TextF.isEventCapture, t.isEventCapture ? 1 : 0).string(TextF.content, t.content)
    .opt(TextF.zOrderIndex, t.zOrderIndex).uint(TextF.textColor, t.textColor);
}
function encImage(i: ImageContainer): PbWriter {
  return new PbWriter().uint(ImageF.x, i.x).uint(ImageF.y, i.y).uint(ImageF.width, i.width).uint(ImageF.height, i.height)
    .uint(ImageF.containerID, i.containerID).string(ImageF.containerName, i.containerName).opt(ImageF.zOrderIndex, i.zOrderIndex);
}
function encMenu(menu: MenuItem[]): PbWriter {
  const w = new PbWriter();
  for (const m of menu) w.message(MenuF.item, new PbWriter().string(MenuItemF.itemName, m.itemName).uint(MenuItemF.itemID, m.itemID));
  return w;
}

function envelope(c: { cmd: number; tag: number }, magic: number, body: PbWriter): Uint8Array {
  return new PbWriter().uint(ROOT.cmd, c.cmd).uint(ROOT.magic, magic & 0xff).message(c.tag, body).finish();
}

export function encodePage(p: Page, magic: number, rebuild = false): Uint8Array {
  validatePage(p);
  const F = rebuild ? RebuildF : CreateF;
  const lists = p.lists ?? [], texts = p.texts ?? [], images = p.images ?? [];
  const w = new PbWriter(1024).uint(F.containerTotalNum, lists.length + texts.length + images.length);
  for (const l of lists) w.message(F.list, encList(l));
  for (const t of texts) w.message(F.text, encText(t));
  for (const i of images) w.message(F.image, encImage(i));
  if (!rebuild) w.uint(CreateF.widgetId, p.widgetId);
  if (p.menu?.length) w.message(F.menu, encMenu(p.menu));
  return envelope(rebuild ? Cmd.RebuildPage : Cmd.CreateStartUpPage, magic, w);
}

export type TextUpgrade = { containerID: number; containerName?: string; content: string; contentOffset?: number; contentLength?: number; textColor?: number };
export function encodeTextUpgrade(u: TextUpgrade, magic: number): Uint8Array {
  const bytes = utf8.encode(u.content);
  check(bytes.length <= Limits.textUpgradeBytes, `text upgrade > ${Limits.textUpgradeBytes} bytes`);
  const w = new PbWriter().uint(TextUpgradeF.containerID, u.containerID).string(TextUpgradeF.containerName, u.containerName)
    .uint(TextUpgradeF.contentOffset, u.contentOffset).uint(TextUpgradeF.contentLength, u.contentLength ?? bytes.length)
    .bytes(TextUpgradeF.content, bytes, true).uint(TextUpgradeF.textColor, u.textColor);
  return envelope(Cmd.TextContainerUpgrade, magic, w);
}

export type ImageFragment = {
  containerID: number; containerName?: string; sessionId: number; totalSize: number;
  compressMode: number; fragmentIndex: number; data: Uint8Array;
};
export function encodeImageFragment(f: ImageFragment, magic: number): Uint8Array {
  check(f.data.length <= Limits.imageFragmentBytes, 'image fragment too large');
  check(f.sessionId !== 0, 'sessionId 0 means "no transfer" in firmware');
  const w = new PbWriter(f.data.length + 64).uint(ImgRawF.containerID, f.containerID).string(ImgRawF.containerName, f.containerName)
    .uint(ImgRawF.sessionId, f.sessionId).uint(ImgRawF.totalSize, f.totalSize).uint(ImgRawF.compressMode, f.compressMode)
    .uint(ImgRawF.fragmentIndex, f.fragmentIndex).uint(ImgRawF.fragmentPacketSize, f.data.length)
    .bytes(ImgRawF.data, f.data, true);
  return envelope(Cmd.ImageRawData, magic, w);
}

export const encodeShutdown = (exitMode: 0 | 1, magic: number) => envelope(Cmd.ShutDownPage, magic, new PbWriter().uint(1, exitMode));
export const encodeHeartbeat = (value: number, magic: number) => envelope(Cmd.HeartBeat, magic, new PbWriter().uint(1, value));
export const encodeAudioControl = (open: boolean, magic: number) => envelope(Cmd.AudioControl, magic, new PbWriter().uint(1, open ? 1 : 0));
export const encodeImuControl = (enable: boolean, reportFrq: number, magic: number) =>
  envelope(Cmd.ImuControl, magic, new PbWriter().uint(1, enable ? 1 : 0).uint(2, reportFrq));

// ---------------------------------------------------------------- decode

export type ListEvent = { kind: 'list'; containerID: number; containerName: string; itemName: string; itemIndex: number; eventType: number };
export type TextEvent = { kind: 'text'; containerID: number; containerName: string; eventType: number };
export type SysEvent = { kind: 'sys'; eventType: number; eventSource: number; imu?: { x: number; y: number; z: number }; exitReason: number };
export type DeviceEvent = ListEvent | TextEvent | SysEvent;

export type Decoded =
  | { type: 'result'; cmd: number; tag: number; magic: number; code: number; extra?: number }
  | { type: 'imageResult'; cmd: number; magic: number; containerID: number; containerName: string; sessionId: number; totalSize: number; compressMode: number; fragmentIndex: number; fragmentPacketSize: number; status: number }
  | { type: 'event'; cmd: number; magic: number; event: DeviceEvent }
  | { type: 'menuStartup'; cmd: number; magic: number; appId: number }
  | { type: 'unknown'; cmd: number; magic: number; tag: number; body?: Uint8Array };

function fieldsOf(b: Uint8Array): Map<number, number | Uint8Array> {
  const m = new Map<number, number | Uint8Array>(); for (const f of pbFields(b)) m.set(f.tag, f.value); return m;
}
const n = (m: Map<number, number | Uint8Array>, t: number) => { const v = m.get(t); return v === undefined ? 0 : pbNum(v); };
const s = (m: Map<number, number | Uint8Array>, t: number) => { const v = m.get(t); return v === undefined ? '' : pbStr(v); };

function decodeDeviceEvent(b: Uint8Array): DeviceEvent {
  for (const f of pbFields(b)) {
    if (!(f.value instanceof Uint8Array)) continue;
    const m = fieldsOf(f.value);
    if (f.tag === DeviceEventF.list)
      return { kind: 'list', containerID: n(m, ListEventF.containerID), containerName: s(m, ListEventF.containerName), itemName: s(m, ListEventF.itemName), itemIndex: n(m, ListEventF.itemIndex), eventType: n(m, ListEventF.eventType) };
    if (f.tag === DeviceEventF.text)
      return { kind: 'text', containerID: n(m, TextEventF.containerID), containerName: s(m, TextEventF.containerName), eventType: n(m, TextEventF.eventType) };
    if (f.tag === DeviceEventF.sys) {
      const imuRaw = m.get(SysEventF.imu);
      let imu: SysEvent['imu'];
      if (imuRaw instanceof Uint8Array) { const i = fieldsOf(imuRaw); imu = { x: i.has(1) ? pbF32(i.get(1)!) : 0, y: i.has(2) ? pbF32(i.get(2)!) : 0, z: i.has(3) ? pbF32(i.get(3)!) : 0 }; }
      return { kind: 'sys', eventType: n(m, SysEventF.eventType), eventSource: n(m, SysEventF.eventSource), imu, exitReason: n(m, SysEventF.exitReason) };
    }
  }
  // proto3: an all-default list/text/sys event can arrive as an empty submessage
  return { kind: 'sys', eventType: 0, eventSource: 0, exitReason: 0 };
}

export function decodeMessage(payload: Uint8Array): Decoded {
  let cmd = 0, magic = 0, tag = 0; let body: Uint8Array | undefined;
  for (const f of pbFields(payload)) {
    if (f.tag === ROOT.cmd) cmd = pbNum(f.value);
    else if (f.tag === ROOT.magic) magic = pbNum(f.value);
    else if (f.value instanceof Uint8Array) { tag = f.tag; body = f.value; }
  }
  const m = body ? fieldsOf(body) : new Map();
  switch (tag) {
    case Cmd.CreateStartUpPageResult.tag: case Cmd.RebuildPageResult.tag: case Cmd.TextContainerUpgradeResult.tag:
    case Cmd.ShutDownPageResult.tag: case Cmd.AudioControlResult.tag: case Cmd.ImuControlResult.tag:
      return { type: 'result', cmd, tag, magic, code: n(m, 1) };
    case Cmd.HeartBeatResult.tag:
      return { type: 'result', cmd, tag, magic, code: n(m, 2), extra: n(m, 1) };
    case Cmd.ImageRawDataResult.tag:
      return { type: 'imageResult', cmd, magic, containerID: n(m, 1), containerName: s(m, 2), sessionId: n(m, 3), totalSize: n(m, 4), compressMode: n(m, 5), fragmentIndex: n(m, 6), fragmentPacketSize: n(m, 7), status: n(m, 8) };
    case Cmd.DeviceEvent.tag:
      return { type: 'event', cmd, magic, event: decodeDeviceEvent(body ?? new Uint8Array(0)) };
    case Cmd.MenuStartup.tag:
      return { type: 'menuStartup', cmd, magic, appId: n(m, 1) };
    default:
      // proto3 drops all-zero submessages' contents but keeps the tag; a result whose
      // body is empty means code 0.
      return { type: 'unknown', cmd, magic, tag, body };
  }
}
