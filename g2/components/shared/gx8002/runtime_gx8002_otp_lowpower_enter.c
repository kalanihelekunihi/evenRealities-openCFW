/* SPDX-License-Identifier: MIT */
/* Recovered package 0x168e0: enter low power only for configuration 0x8002.
 * The OTP helper return is deliberately ignored, as in the stock caller.
 * Architectural synchronization and sleep use explicit instructions. */
#include <stdint.h>
extern int open_cfw_gx8002_flash_otp_configuration(uint32_t *);
extern void open_cfw_gx8002_clock_switch_1m(void);
#define REG(address) (*(volatile uint32_t *)(address))
void open_cfw_gx8002_otp_lowpower_enter(void)
{
    uint32_t configuration=0;
    open_cfw_gx8002_flash_otp_configuration(&configuration);
    if (configuration!=0x8002) return;
    /* Keep the common clear mask in a register across the two updates.
     * The empty constraint emits no instructions or binary payload. */
    uint32_t clear_mask=0x00038100u;
    __asm__("" : "+r"(clear_mask));
    uint32_t value=REG(0xa0000024u);
    value=(value&~clear_mask)|0x00006800u;
    REG(0xa0000024u)=value;
    value=REG(0xa0000028u);
    value=(value&~clear_mask)|0x00006000u;
    REG(0xa0000028u)=value;
    REG(0xa0000038u)&=~0x10u;
    REG(0xa0000034u)=15;
    open_cfw_gx8002_clock_switch_1m();
    __asm__ volatile("sync\n\tsync" ::: "memory");
    REG(0xe000f004u)=5;
    __asm__ volatile("sync\n\tsync" ::: "memory");
    REG(0xa0000000u)=1;
    __asm__ volatile("doze" ::: "memory");
}
