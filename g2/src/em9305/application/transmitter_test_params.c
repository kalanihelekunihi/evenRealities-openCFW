/* SPDX-License-Identifier: MIT
 * Stock 0x333b48 (g2-2.2.6.10 firmware_ble_em9305.bin; the tail of scheduler_base_interval_gap in stock_residual_code.c): parameter check of the
 * em_system transmitter test commands. `params` is the command payload, `plen` its length, `mode` 0 or 1 (ordinary test) or 2 (the extended command with the
 * additional parameters at index 6..8); every other mode is rejected. Returns 1 if the parameters are acceptable, 0 if not.
 * params[0] < 9, params[1] < 0x28, params[3] < 0xf when params[0] is 0, params[4] in 1..5, and params[5], a signed byte (transmit power), is at most 0x14.
 * Mode 0/1 also needs plen == 6 and rejects params[4] == 5 with params[0] == 0 and params[2] >= 0x7e. Mode 2 only enforces the power limit when plen >= 5, rejects -128,
 * allows params[6] == 0 or 2..0x14, params[7] < 3 and params[8] in 2..75.
 */
#include <stdint.h>

uint32_t opencfw_em9305_stock_333b48(const uint8_t *params, uint32_t plen, uint32_t mode)
{
  if (mode < 2u) {
    if (plen == 6u && params[0] < 9u && params[1] < 0x28u && (params[0] != 0u || params[3] < 0xfu) &&
        (uint32_t)params[4] - 1u < 5u && (uint32_t)params[5] - 0x15u > 0x6bu) {
      if (params[4] == 5u && params[0] == 0u && params[2] >= 0x7eu) return 0u;
      return 1u;
    }
    return 0u;
  }
  if (mode != 2u) return 0u;
  if (params[0] >= 9u || params[1] >= 0x28u) return 0u;
  if (params[0] == 0u && params[3] >= 0xfu) return 0u;
  if ((uint32_t)params[4] - 1u >= 5u) return 0u;
  int32_t power = (int8_t)params[5];
  if (plen >= 5u && power > 0x14) return 0u;
  if (power == -128) return 0u;
  uint32_t p6 = params[6];
  if (p6 != 0u && (p6 == 1u || p6 >= 0x15u)) return 0u;
  if (params[7] >= 3u) return 0u;
  return (uint8_t)(params[8] - 76u) > 181u;
}

/* ----  * Stock 0x333a94 (g2-2.2.6.10 firmware_ble_em9305.bin; scheduler_base_interval_gap in stock_residual_code.c): the em_system transmitter test command
 * (EMSRC_TransmitterTest). `params` (plen bytes) is checked by 0x333b48 in mode 0, which returns 0x12 for bad parameters.
 * The packet length limit comes from 0x3047fc. If params[0] is non-zero, *len = 1 and EMSystem_TransmitCM(min(limit, (int8)params[5]), params[0], params[1], params[4],
 * resp, len) runs, and resp[4] is set to the limit on success. Otherwise a 20-byte command record (bytes 2..5 = params[1..4], byte 8 = 2, byte 16 = (int8)params[5] if it is at most
 * the limit, else 0x7f) is run by 0x30e120, then resp[4] = limit, resp[5] = min(radio_status(1), (int8)params[5]) and *len grows by 2. Returns the status of the command.
 * FLAG: the stock code passes the leftover result of the parameter check (always 1 here) to the packet limit routine, written as 1; bytes 9..11 and 17..19 of the
 * command record are never initialised in the stock code and are left alone here.
 */

extern uint32_t opencfw_em9305_common_packet_limit_3047fc(uint32_t incoming);
extern uint32_t opencfw_em9305_stock_305ab4(int32_t a, uint32_t b, uint32_t c, uint32_t d, uint8_t *resp, uint8_t *len);
extern uint32_t opencfw_em9305_command_30e120(uintptr_t command);
extern uint32_t opencfw_em9305_radio_status_311a00(uint32_t query);

static int32_t min_s32(int32_t a, int32_t b) { return a < b ? a : b; }

uint32_t opencfw_em9305_stock_333a94(uint32_t plen, const uint8_t *params, uint8_t *resp, uint8_t *len)
{
  if (opencfw_em9305_stock_333b48(params, plen, 0u) == 0u) return 0x12u;
  int32_t power = (int8_t)params[5];
  uint32_t limit = opencfw_em9305_common_packet_limit_3047fc(1u);
  if (params[0] != 0u) {
    *len = 1u;
    uint32_t r = opencfw_em9305_stock_305ab4(min_s32((int32_t)limit, power), params[0], params[1], params[4], resp, len);
    if (r != 0u) return r;
    resp[4] = (uint8_t)limit;
    return 0u;
  }
  uint8_t cmd[20] __attribute__((aligned(4)));
  cmd[0] = 0u; cmd[1] = 0u; cmd[6] = 0u; cmd[7] = 0u;
  cmd[12] = 0u; cmd[13] = 0u; cmd[14] = 0u; cmd[15] = 0u;
  *len = 1u;
  cmd[8] = 2u;
  cmd[5] = params[4];
  cmd[4] = params[3];
  cmd[3] = params[2];
  cmd[2] = params[1];
  cmd[16] = (power <= (int32_t)limit) ? (uint8_t)power : 0x7fu;
  uint32_t r = opencfw_em9305_command_30e120((uintptr_t)cmd);
  if (r != 0u) return r;
  uint32_t prev = opencfw_em9305_radio_status_311a00(1u);
  resp[4] = (uint8_t)limit;
  resp[5] = (uint8_t)min_s32((int32_t)prev, power);
  *len = (uint8_t)(*len + 2u);
  return 0u;
}
