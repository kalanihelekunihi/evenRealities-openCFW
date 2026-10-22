/* SPDX-License-Identifier: MIT
 * Resident 0x10025664 gx_dcache_clean_range. The stock literal at
 * 0x100256bc is 0xe000f000; its +4 command register receives one write
 * per 16-byte line. The authenticated request caller supplies 16 bytes.
 */
#include <stdint.h>

/* Stock 0x10025664 (gx_dcache_clean_range) */
void g2_codec_header_sync(void *header, uint32_t bytes)
{
    volatile uint32_t *const command =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004);
    uint32_t line = ((uint32_t)(uintptr_t)header & ~UINT32_C(15)) | 8u;
    while (bytes >= 128u) {
        command[0] = line;
        command[0] = line + 16u;
        command[0] = line + 32u;
        command[0] = line + 48u;
        command[0] = line + 64u;
        command[0] = line + 80u;
        command[0] = line + 96u;
        command[0] = line + 112u;
        line += 128u;
        bytes -= 128u;
    }
    while (bytes != 0u) {
        command[0] = line;
        line += 16u;
        bytes = bytes > 16u ? bytes - 16u : 0u;
    }
}
