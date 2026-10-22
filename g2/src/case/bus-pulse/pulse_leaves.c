/* SPDX-License-Identifier: MIT
 * Stock 0x0800a1ac..0x0800a224 and 0x0800a270..0x0800a2a2: constant-delay
 * single-wire pulse leaves. The callers 0x0800a188/0x0800a19a/0x08002cb8 are
 * sourced with these bodies inlined; these are the stand-alone stock entries.
 * Channel "4" is GPIOB pin mask 4 (0x50000400), channel "8" is GPIOA pin
 * mask 8 (0x50000000); the delay leaves take a loop count.
 */
#include <stdint.h>

extern void case_boot_gpio_a4_output(void);           /* 0x0800ba84 */
extern void case_boot_gpio_a4_high(void);             /* 0x0800bac4 */
extern void case_boot_gpio_a4_low(void);              /* 0x0800bae8 */
extern void case_bus_drive_b(void);                   /* 0x0800baa4 */
extern void case_bus_drive_a(void);                   /* 0x0800bad8 */
extern void case_bus_drive_c(void);                   /* 0x0800bafc */
extern void case_boot_short_delay_a794(uint32_t count); /* 0x0800a794 */
extern void case_boot_short_delay_a7a2(uint32_t count); /* 0x0800a7a2 */

/* Channel-4 low pulse of 23 delay counts. */
/* Stock 0x0800A1AC (case_pulse4_short) */
void case_pulse4_short(void)
{
    case_boot_gpio_a4_high();
    case_boot_gpio_a4_output();
    case_boot_gpio_a4_high();
    case_boot_gpio_a4_low();
    case_boot_short_delay_a794(23u);
    case_boot_gpio_a4_high();
}

/* Channel-8 low pulse of 23 delay counts. */
/* Stock 0x0800A1CA (case_pulse8_short) */
void case_pulse8_short(void)
{
    case_bus_drive_a();
    case_bus_drive_b();
    case_bus_drive_a();
    case_bus_drive_c();
    case_boot_short_delay_a7a2(23u);
    case_bus_drive_a();
}

/* Channel-4 low pulse of 90 delay counts. */
/* Stock 0x0800A1E8 (case_pulse4_long) */
void case_pulse4_long(void)
{
    case_boot_gpio_a4_high();
    case_boot_gpio_a4_output();
    case_boot_gpio_a4_high();
    case_boot_gpio_a4_low();
    case_boot_short_delay_a794(90u);
    case_boot_gpio_a4_high();
}

/* Channel-8 low pulse of 90 delay counts. */
/* Stock 0x0800A206 (case_pulse8_long) */
void case_pulse8_long(void)
{
    case_bus_drive_a();
    case_bus_drive_b();
    case_bus_drive_a();
    case_bus_drive_c();
    case_boot_short_delay_a7a2(90u);
    case_bus_drive_a();
}

/* High for 350 counts, then low for 40 x 350 counts.
 * The first delay runs before the line is driven low (unlike 0x0800a2e6). */
/* Stock 0x0800A270 (case_pulse4_train_pre_delay) */
void case_pulse4_train_pre_delay(void)
{
    case_boot_gpio_a4_high();
    case_boot_gpio_a4_output();
    case_boot_gpio_a4_high();
    case_boot_short_delay_a794(350u);
    case_boot_gpio_a4_low();
    for (uint8_t i = 0u; i < 40u; i = (uint8_t)(i + 1u))
        case_boot_short_delay_a794(350u);
    case_boot_gpio_a4_high();
}
