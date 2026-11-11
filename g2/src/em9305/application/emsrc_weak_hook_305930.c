/* SPDX-License-Identifier: MIT
 * Stock 0x305930 emsrc_weak_hook_305930 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Default body of an overridable SDK hook called by EMSRC_EmCoreReceiverTestEnd and EMSRC_EmCoreReceiver154TestEnd: returns 0xc (command disallowed). Name inferred from the caller; the real symbol name is not recoverable.
 */
#include <stdint.h>
uint32_t opencfw_em9305_emsrc_weak_hook_305930(void) { return 0xcu; }
