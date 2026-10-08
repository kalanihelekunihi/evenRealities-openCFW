/* SPDX-License-Identifier: MIT; recovered42ddda conditional handle clear. */
#include <stdint.h>
extern void opencfw_boot_dfu_thread_terminate(uint32_t);
uint32_t opencfw_boot_dfu_thread_deinit_native(void) {
 volatile uint32_t *h=(volatile uint32_t *)(uintptr_t)0x200004d4u;
 if(*h){opencfw_boot_dfu_thread_terminate(*h);*h=0;}
 return 0;
}
