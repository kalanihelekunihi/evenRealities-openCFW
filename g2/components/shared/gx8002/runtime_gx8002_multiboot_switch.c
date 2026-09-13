/* SPDX-License-Identifier: MIT */
/* SwitchAnotherFirmeware from pinned lvp_system_init.c lineage. */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_multiboot_marker;
extern void gx_dcache_clean_range(void *,unsigned);
extern void gx_reboot(void);
extern int printf(const char *,...);
const char open_cfw_gx8002_multiboot_first[] __attribute__((section(".rodata.first"),aligned(1))) = "boot from first firmware\n";
const char open_cfw_gx8002_multiboot_second[] __attribute__((section(".rodata.second"),aligned(1))) = "boot from second firmware\n";
void open_cfw_gx8002_multiboot_switch(void)
{
    if(open_cfw_gx8002_multiboot_marker==UINT32_C(0xaabbccdd)) {
        printf(open_cfw_gx8002_multiboot_first);
        open_cfw_gx8002_multiboot_marker=0;
    } else {
        printf(open_cfw_gx8002_multiboot_second);
        open_cfw_gx8002_multiboot_marker=UINT32_C(0xaabbccdd);
    }
    gx_dcache_clean_range((void *)&open_cfw_gx8002_multiboot_marker,16);
    gx_reboot();
}
