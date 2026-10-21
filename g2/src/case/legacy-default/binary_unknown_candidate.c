/* SPDX-License-Identifier: MIT
 * Isolated stock 0x08000e88/0x08000f22 unknown-command fallback.
 * Contract: caller has classified this command as unhandled.
 */
#include <stdint.h>
extern uint32_t case_binary_logger(const char *, ...);
uint32_t case_binary_unknown_candidate(const uint8_t *command, uint32_t length)
{
    (void)length;
    uint32_t state = *(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (state == 0) {
        case_binary_logger("dst(box) cannot parse cmd: %02x", command[0]);
        return case_binary_logger("\r\n");
    }
    return state;
}
