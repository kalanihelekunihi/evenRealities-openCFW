/* SPDX-License-Identifier: MIT */
/* Recovered board entry and four fixed register writes. The inline branch
 * expresses reason >= 2 directly within the original 20-byte envelope. */
#include <stdint.h>
extern unsigned int open_cfw_gx8002_reset_reason(void);
extern void *open_cfw_gx8002_flash_initialize(void);

__attribute__((noinline)) void open_cfw_gx8002_board_register_initialize(void)
{
    *(volatile uint32_t *)0xa0005040u = 0x59;
    *(volatile uint32_t *)0xa0005044u = 0x59;
    *(volatile uint32_t *)0xa0005048u = 0x59;
    *(volatile uint32_t *)0xa000504cu = 0x59;
}

void open_cfw_gx8002_board_initialize(void)
{
    unsigned reason=open_cfw_gx8002_reset_reason();
    __asm__ goto ("cmphsi %0, 2\n\tbf %l[registers]" : : "r"(reason) : "cc" : registers);
    open_cfw_gx8002_flash_initialize();
registers:
    open_cfw_gx8002_board_register_initialize();
}
