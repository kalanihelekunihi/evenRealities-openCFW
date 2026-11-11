/* SPDX-License-Identifier: MIT
 * Stock 0x3335f4 (receiverTestCheckParameters), g2-2.2.6.10 firmware_ble_em9305.bin. Validates the parameter bytes of an LE receiver-test command and
 * returns 1 when acceptable, 0 otherwise. `mode` is 0 (6 bytes), 1 (7 bytes) or 2 (the longer parameter list, length not checked); any other mode
 * returns 0. Common checks: p[0] < 0x28 (channel) and p[1]-1 < 5 (PHY). Mode 0 needs only those; mode 1 also needs p[6] < 2; mode 2 needs
 * p[6] < 2, p[7] == 0 or 2..0x14, p[8] < 3, p[9]-1 < 2 and (uint8_t)(p[10]-76) > 181 (i.e. p[10] in 2..75).
 * FLAGS: field meanings are inferred from the HCI LE enhanced receiver test layout and are not verified; the parameter names are guesses; the p[10]
 * range test mirrors stock (extb of the subtraction compared unsigned with 181).
 */
#include <stdint.h>

uint32_t opencfw_em9305_stock_3335f4(const uint8_t *p, uint32_t length, uint32_t mode)
{
  if (mode == 2u) {
    if (p[0] >= 0x28u) return 0u;
    if ((uint32_t)p[1] - 1u >= 5u) return 0u;
    if (p[6] >= 2u) return 0u;
    uint32_t v = p[7];
    if (v != 0u) {
      if (v == 1u || v >= 0x15u) return 0u;
    }
    if (p[8] >= 3u) return 0u;
    if ((uint32_t)p[9] - 1u >= 2u) return 0u;
    return (uint8_t)(p[10] - 76u) > 181u ? 1u : 0u;
  }
  if (mode == 1u) {
    if (length != 7u) return 0u;
    if (p[0] >= 0x28u) return 0u;
    if ((uint32_t)p[1] - 1u >= 5u) return 0u;
    return p[6] < 2u ? 1u : 0u;
  }
  if (mode != 0u || length != 6u) return 0u;
  if (p[0] >= 0x28u) return 0u;
  return (uint32_t)p[1] - 1u < 5u ? 1u : 0u;
}
