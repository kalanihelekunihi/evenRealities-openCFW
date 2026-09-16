/* SPDX-License-Identifier: MIT */
/* Backup package 0x412b8. The first pin/function pair is constant (0,1),
 * even if the initialization helper changes the table. */
#include <stdint.h>
extern int open_cfw_gx8002_padmux_init(const void *,int);
extern int open_cfw_gx8002_padmux_check(int,int);
extern int open_cfw_gx8002_gpio_set_direction(unsigned,int);
extern int open_cfw_gx8002_printf(const char *,...);
extern void open_cfw_gx8002_board_pin_setup(void);
void open_cfw_gx8002_backup_board_pin_initialize(void)
{
    open_cfw_gx8002_padmux_init((const void *)0x10012ecc,13);
    const volatile uint8_t *cursor=(const volatile uint8_t *)0x10012ece;
    unsigned pin=0,function=1;
    for (;;) {
        if (open_cfw_gx8002_padmux_check(pin,function))
            open_cfw_gx8002_printf((const char *)0x10012f38,pin);
        if (function==(pin==2 ? 0u:1u))
            open_cfw_gx8002_gpio_set_direction(pin,0);
        if (cursor==(const volatile uint8_t *)0x10012ee6) break;
        pin=cursor[0];function=cursor[1];cursor+=2;
    }
    open_cfw_gx8002_board_pin_setup();
    *(volatile uint32_t *)0x200176d8=1;
}
