// Image payload helpers. The firmware (C3-evenhub-decompress + common image container
// set_data) wants a Windows BMP, 4 bits per pixel, exactly the container's width x height,
// optionally RLE- or LZ4-block-compressed, delivered in strictly sequential fragments.
import { Compress, Limits } from './schema.ts';

/** Build a 16-level grayscale 4-bpp bottom-up BMP from 8-bit luminance pixels (row-major, top row first). */
export function encodeBmp4(gray: Uint8Array, width: number, height: number): Uint8Array {
  if (gray.length !== width * height) throw new RangeError('gray length != width*height');
  const stride = Math.ceil(Math.ceil(width / 2) / 4) * 4;
  const off = 14 + 40 + 16 * 4;
  const size = off + stride * height;
  const out = new Uint8Array(size); const dv = new DataView(out.buffer);
  out[0] = 0x42; out[1] = 0x4d; dv.setUint32(2, size, true); dv.setUint32(10, off, true);
  dv.setUint32(14, 40, true); dv.setInt32(18, width, true); dv.setInt32(22, height, true);
  dv.setUint16(26, 1, true); dv.setUint16(28, 4, true); dv.setUint32(34, stride * height, true);
  dv.setUint32(46, 16, true);
  for (let i = 0; i < 16; i++) { const v = i * 17; out.set([v, v, v, 0], 54 + i * 4); }
  for (let y = 0; y < height; y++) {
    const row = off + (height - 1 - y) * stride;
    for (let x = 0; x < width; x++) {
      const q = gray[y * width + x] >> 4;
      out[row + (x >> 1)] |= x & 1 ? q : q << 4;
    }
  }
  return out;
}

/** RLE as decoded by the firmware: repeated {count (1..255), byte} pairs. */
export function rleEncode(src: Uint8Array): Uint8Array {
  const out: number[] = [];
  for (let i = 0; i < src.length;) {
    let n = 1; while (n < 255 && i + n < src.length && src[i + n] === src[i]) n++;
    out.push(n, src[i]); i += n;
  }
  return Uint8Array.from(out);
}
export function rleDecode(src: Uint8Array): Uint8Array {
  const out: number[] = [];
  for (let i = 0; i + 1 < src.length; i += 2) for (let k = 0; k < src[i]; k++) out.push(src[i + 1]);
  return Uint8Array.from(out);
}

/** Greedy LZ4 *block* compressor (format accepted by LZ4_decompress_safe). */
export function lz4BlockEncode(src: Uint8Array): Uint8Array {
  const out: number[] = []; const table = new Int32Array(1 << 16).fill(-1);
  const MINMATCH = 4, LASTLITERALS = 5, MFLIMIT = 12;
  const hash = (i: number) => (Math.imul(src[i] | (src[i + 1] << 8) | (src[i + 2] << 16) | (src[i + 3] << 24), 2654435761) >>> 16);
  const len = (n: number) => { while (n >= 255) { out.push(255); n -= 255; } out.push(n); };
  let anchor = 0, i = 0;
  const end = src.length - MFLIMIT;
  while (i < end) {
    const h = hash(i); const ref = table[h]; table[h] = i;
    if (ref >= 0 && i - ref <= 0xffff && src[ref] === src[i] && src[ref + 1] === src[i + 1] && src[ref + 2] === src[i + 2] && src[ref + 3] === src[i + 3]) {
      let m = MINMATCH; while (i + m < src.length - LASTLITERALS && src[ref + m] === src[i + m]) m++;
      const lit = i - anchor; const ml = m - MINMATCH;
      out.push((Math.min(lit, 15) << 4) | Math.min(ml, 15));
      if (lit >= 15) len(lit - 15);
      for (let k = anchor; k < i; k++) out.push(src[k]);
      const d = i - ref; out.push(d & 0xff, d >> 8);
      if (ml >= 15) len(ml - 15);
      i += m; anchor = i;
    } else i++;
  }
  const lit = src.length - anchor;
  out.push(Math.min(lit, 15) << 4); if (lit >= 15) len(lit - 15);
  for (let k = anchor; k < src.length; k++) out.push(src[k]);
  return Uint8Array.from(out);
}
export function lz4BlockDecode(src: Uint8Array, maxOut: number): Uint8Array {
  const out = new Uint8Array(maxOut); let o = 0, i = 0;
  const rd = () => { let n = 0, b: number; do { b = src[i++]; n += b; } while (b === 255); return n; };
  while (i < src.length) {
    const t = src[i++]; let lit = t >> 4; if (lit === 15) lit += rd();
    if (o + lit > maxOut) throw new Error('lz4: overflow');
    out.set(src.subarray(i, i + lit), o); o += lit; i += lit;
    if (i >= src.length) break;
    const d = src[i] | (src[i + 1] << 8); i += 2; if (!d || d > o) throw new Error('lz4: bad offset');
    let ml = (t & 15); if (ml === 15) ml += rd(); ml += 4;
    if (o + ml > maxOut) throw new Error('lz4: overflow');
    for (let k = 0; k < ml; k++, o++) out[o] = out[o - d];
  }
  return out.slice(0, o);
}

export type CompressChoice = 'none' | 'rle' | 'lz4' | 'auto';

/**
 * Prepare an image transfer: pick the smallest encoding and split it into
 * <= 4 KiB sequential fragments. totalSize is capped at width*height because
 * the firmware's receive buffer is width*height bytes and it does not bounds-check
 * the first fragment copy.
 */
export function planImage(bmp: Uint8Array, width: number, height: number, choice: CompressChoice = 'auto', fragmentBytes: number = Limits.imageFragmentDefault) {
  const cands: { mode: number; data: Uint8Array }[] = [];
  if (choice === 'none' || choice === 'auto') cands.push({ mode: Compress.NONE, data: bmp });
  if (choice === 'rle' || choice === 'auto') cands.push({ mode: Compress.RLE, data: rleEncode(bmp) });
  if (choice === 'lz4' || choice === 'auto') cands.push({ mode: Compress.LZ4, data: lz4BlockEncode(bmp) });
  const best = cands.reduce((a, b) => (b.data.length < a.data.length ? b : a));
  const cap = width * height;
  if (best.data.length > cap) throw new RangeError(`encoded image ${best.data.length} B exceeds firmware buffer ${cap} B (w*h)`);
  if (bmp.length > cap && best.mode !== Compress.NONE) {
    // decompressed output must also fit; a 4bpp BMP is ~w*h/2 + 118, so this only trips for tiny images
    throw new RangeError('decompressed BMP exceeds w*h buffer');
  }
  const fragSize = Math.min(fragmentBytes, Limits.imageFragmentBytes);
  const fragments: Uint8Array[] = [];
  for (let o = 0; o < best.data.length; o += fragSize) fragments.push(best.data.subarray(o, o + fragSize));
  return { compressMode: best.mode, totalSize: best.data.length, fragments };
}
