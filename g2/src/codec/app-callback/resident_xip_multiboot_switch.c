/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10207a80 multiboot selector. Stock literal pool
 * fixes state at 0x20033ffc and sentinel 0xaabbccdd; both log strings
 * are exact source literals from XIP 0x1020b148 and 0x1020b162.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void g2_codec_header_sync(void *, uint32_t);
extern __attribute__((noreturn)) void gx8002_xip_reboot_102067b8(void);

void gx8002_xip_multiboot_switch_10207a80(void)
{
    volatile uint32_t *const selector =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20033ffc);
    if (*selector == UINT32_C(0xaabbccdd)) {
        (void)gx8002_xip_tws_publish_10206c24(
            "boot from first firmware\n");
        *selector = 0u;
    } else {
        (void)gx8002_xip_tws_publish_10206c24(
            "boot from second firmware\n");
        *selector = UINT32_C(0xaabbccdd);
    }
    g2_codec_header_sync((void *)selector, 16u);
    gx8002_xip_reboot_102067b8();
}
