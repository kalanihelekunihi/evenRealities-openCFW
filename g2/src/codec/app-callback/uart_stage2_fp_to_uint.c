/* SPDX-License-Identifier: MIT
 * Stock stage2 0x100073c8: binary64 to uint32. Native compares against
 * 0x41e0000000000000 (2^31), subtracts that threshold on the high path,
 * converts the remainder to signed 32-bit, then adds 0x80000000.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_fp_compare_words_7a48(
    uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_uart_stage2_fp_to_int_7a88(uint32_t, uint32_t);
extern uint64_t gx8002_uart_stage2_fp_sub_words_76f4(
    uint32_t, uint32_t, uint32_t, uint32_t);

uint32_t gx8002_uart_stage2_fp_to_uint_73c8(
    uint32_t low, uint32_t high)
{
    if (gx8002_uart_stage2_fp_compare_words_7a48(
            low, high, 0u, UINT32_C(0x41e00000)) < 0)
        return gx8002_uart_stage2_fp_to_int_7a88(low, high);
    uint64_t shifted = gx8002_uart_stage2_fp_sub_words_76f4(
        low, high, 0u, UINT32_C(0x41e00000));
    return gx8002_uart_stage2_fp_to_int_7a88(
        (uint32_t)shifted, (uint32_t)(shifted >> 32)) + UINT32_C(0x80000000);
}
