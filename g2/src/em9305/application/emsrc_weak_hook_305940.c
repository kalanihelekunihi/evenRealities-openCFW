/* SPDX-License-Identifier: MIT
 * Stock 0x305940 emsrc_weak_hook_305940 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Default body of an overridable SDK hook called by EMSRC_EmCoreTransmitterTestEnd: returns 0xc (command disallowed). Name inferred from the caller; the real symbol name is not recoverable.
 */
#include <stdint.h>
uint32_t opencfw_em9305_emsrc_weak_hook_305940(void) { return 0xcu; }
