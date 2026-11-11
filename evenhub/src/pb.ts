// Minimal protobuf wire codec (varint, fixed32, length-delimited). No reflection,
// no generated classes: the EvenHub schema is small and fixed by the firmware.

export class PbWriter {
  private buf: Uint8Array;
  private len = 0;
  constructor(initial = 256) { this.buf = new Uint8Array(initial); }
  private ensure(n: number): void {
    if (this.len + n <= this.buf.length) return;
    let cap = this.buf.length * 2;
    while (cap < this.len + n) cap *= 2;
    const nb = new Uint8Array(cap); nb.set(this.buf.subarray(0, this.len)); this.buf = nb;
  }
  rawVarint(v: number): this {
    if (v < 0 || !Number.isInteger(v) || v > 0xffffffff) throw new RangeError(`uint32 out of range: ${v}`);
    this.ensure(5);
    while (v > 0x7f) { this.buf[this.len++] = (v & 0x7f) | 0x80; v = Math.floor(v / 128); }
    this.buf[this.len++] = v;
    return this;
  }
  /** proto3 semantics: zero / undefined is not emitted. */
  uint(tag: number, v: number | undefined): this {
    if (v === undefined || v === 0) return this;
    return this.rawVarint((tag << 3) | 0).rawVarint(v);
  }
  /** Always emits, even when zero (needed for oneof members / explicit presence). */
  uintAlways(tag: number, v: number): this { return this.rawVarint((tag << 3) | 0).rawVarint(v); }
  /** Explicit presence: emits whenever defined, including 0. */
  opt(tag: number, v: number | undefined): this { return v === undefined ? this : this.uintAlways(tag, v); }
  fixed32f(tag: number, v: number | undefined): this {
    if (v === undefined || v === 0) return this;
    this.rawVarint((tag << 3) | 5); this.ensure(4);
    new DataView(this.buf.buffer, this.buf.byteOffset + this.len, 4).setFloat32(0, v, true);
    this.len += 4; return this;
  }
  bytes(tag: number, b: Uint8Array | undefined, always = false): this {
    if (b === undefined || (b.length === 0 && !always)) return this;
    this.rawVarint((tag << 3) | 2).rawVarint(b.length); this.ensure(b.length);
    this.buf.set(b, this.len); this.len += b.length; return this;
  }
  string(tag: number, s: string | undefined): this {
    return s === undefined ? this : this.bytes(tag, utf8.encode(s));
  }
  message(tag: number, w: PbWriter, always = true): this { return this.bytes(tag, w.finish(), always); }
  finish(): Uint8Array { return this.buf.slice(0, this.len); }
}

export const utf8 = new TextEncoder();
const utf8d = new TextDecoder('utf-8', { fatal: false });

export type PbField = { tag: number; wire: 0 | 1 | 2 | 5; value: number | Uint8Array };

export function* pbFields(b: Uint8Array): Generator<PbField> {
  let p = 0;
  const varint = (): number => {
    let r = 0, mul = 1, byte: number;
    do {
      if (p >= b.length) throw new Error('pb: truncated varint');
      byte = b[p++]; r += (byte & 0x7f) * mul; mul *= 128;
      if (mul > 2 ** 63) throw new Error('pb: varint too long');
    } while (byte & 0x80);
    return r;
  };
  while (p < b.length) {
    const key = varint(); const tag = Math.floor(key / 8); const wire = key & 7;
    if (tag === 0) throw new Error('pb: tag 0');
    if (wire === 0) yield { tag, wire, value: varint() };
    else if (wire === 2) {
      const n = varint(); if (p + n > b.length) throw new Error('pb: truncated bytes');
      yield { tag, wire, value: b.subarray(p, p + n) }; p += n;
    } else if (wire === 5) {
      if (p + 4 > b.length) throw new Error('pb: truncated fixed32');
      yield { tag, wire, value: b.subarray(p, p + 4) }; p += 4;
    } else if (wire === 1) {
      if (p + 8 > b.length) throw new Error('pb: truncated fixed64');
      yield { tag, wire, value: b.subarray(p, p + 8) }; p += 8;
    } else throw new Error(`pb: unsupported wire type ${wire}`);
  }
}

export const pbStr = (v: number | Uint8Array): string => (typeof v === 'number' ? String(v) : utf8d.decode(v));
export const pbF32 = (v: number | Uint8Array): number =>
  typeof v === 'number' ? v : new DataView(v.buffer, v.byteOffset, 4).getFloat32(0, true);
export const pbNum = (v: number | Uint8Array): number => (typeof v === 'number' ? v : 0);
