/* SPDX-License-Identifier: MIT
 * Stock 0x30ef44 (NVM_InitCopy), 0x333c24 (validate) and 0x31435c (_initdatCopy), g2-2.2.6.10 firmware_ble_em9305.bin.
 * The initialisation record (opencfw_em9305_ini_record_335820) starts with the bytes 'I' 'N' 'I' and a version byte. validate() returns 1 for a bad
 * signature, 2 for a version of 4 or more and 0 otherwise. Versions below 3 have the entries at +4 and use _initdatCopy; version 3 has a copy
 * routine pointer at +4 and the entries at +8. Each entry is {destination address, signed size} followed, for a positive size, by the data padded to a
 * multiple of 4. A size of 0 with a zero address ends the list; a negative size clears -size bytes at the address. An entry is skipped when its
 * destination lies in 0x801000..0x80e978 and `ram_flag` is 0, or in 0x1ff000..0x200000 and `high_flag` is 0, or, for `full == 0`, inside
 * 0x801000..(ROM 0x1030dc() + 0x801000). The copy routine is called with (data, size, destination, &out).
 * FLAG: ROM 0x1030dc is named by address only and its role is unknown (stock leaves the version byte in r0 when it calls it; no arguments are
 * modelled, and the only caller passes full == 1, so this path is not reached). The weak symbol test below mirrors stock comparing the link-time
 * image end address with 0 before running anything; why stock does so is not known.
 */
#include <stdint.h>

extern void *opencfw_em9305_memset(void *dst, uint32_t value, uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t em9305_rom_1030dc(void);
extern char opencfw_em9305_image_end[] __attribute__((weak));

typedef void (*ini_copy_fn)(const void *data, int32_t size, void *destination, int32_t *out);

uint32_t opencfw_em9305_stock_333c24(const uint8_t *record)
{
  if (record[0] != 'I' || record[1] != 'N' || record[2] != 'I') return 1u;
  return record[3] >= 4u ? 2u : 0u;
}

void opencfw_em9305_stock_31435c(const void *data, int32_t size, void *destination, int32_t *out)
{
  (void)opencfw_em9305_memcpy(destination, data, (uint32_t)size);
  *out = size;
}

uint32_t opencfw_em9305_stock_30ef44(const uint8_t *record, uint32_t ram_flag, uint32_t full, uint32_t high_flag)
{
  int32_t out;
  if (opencfw_em9305_image_end == 0) return 0u;
  uint32_t status = opencfw_em9305_stock_333c24(record);
  if (status != 0u) return status;
  ini_copy_fn copy;
  const uint8_t *p;
  if (record[3] < 3u) {
    p = record + 4;
    copy = opencfw_em9305_stock_31435c;
  } else {
    copy = *(const ini_copy_fn *)(record + 4);
    p = record + 8;
  }
  uint32_t limit = 0u;
  if (full == 0u) limit = em9305_rom_1030dc() + 0x801000u;
  for (;;) {
    uint32_t address = ((const uint32_t *)p)[0];
    int32_t size = (int32_t)((const uint32_t *)p)[1];
    if (size == 0) {
      if (address == 0u) return 0u;
      p += 8;
      continue;
    }
    int skip;
    if (address >= 0x801000u && address < 0x80e978u && ram_flag == 0u) skip = 1;
    else if (address >= 0x1ff000u && address < 0x200000u && high_flag == 0u) skip = 1;
    else skip = !(address >= limit || address < 0x801000u || full != 0u);
    if (!skip) {
      if (size >= 1) {
        copy(p + 8, size, (void *)(uintptr_t)address, &out);
      } else {
        (void)opencfw_em9305_memset((void *)(uintptr_t)address, 0u, (uint32_t)(-size));
        p += 8;
        continue;
      }
    }
    if (size >= 1) p += ((uint32_t)size + 3u) & ~3u;
    p += 8;
  }
}
