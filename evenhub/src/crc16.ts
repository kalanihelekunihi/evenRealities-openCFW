// CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF, no reflection, no xorout).
// Stock leaf at 0x0049ACD4 (g2/docs/reference/protocols.md section 3).
const TABLE = (() => {
  const t = new Uint16Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i << 8;
    for (let k = 0; k < 8; k++) c = c & 0x8000 ? ((c << 1) ^ 0x1021) & 0xffff : (c << 1) & 0xffff;
    t[i] = c;
  }
  return t;
})();

export function crc16CcittFalse(data: Uint8Array, init = 0xffff): number {
  let crc = init;
  for (let i = 0; i < data.length; i++) crc = ((crc << 8) & 0xffff) ^ TABLE[((crc >> 8) ^ data[i]) & 0xff];
  return crc;
}
