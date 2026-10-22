/* SPDX-License-Identifier: MIT
 * CASE sensor IRQ error recovery, native 0x080086f4. Native 0x6776 is an
 * independently observed BX LR leaf used for final notification.
 */
#include <stdint.h>
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint32_t mask(void){uint32_t x;__asm volatile("mrs %0, primask":"=r"(x));return x;}
static void setmask(uint32_t x){__asm volatile("msr primask, %0"::"r"(x):"memory");}
static void clear_locked(uint32_t a,uint32_t bits)
{uint32_t m=mask();setmask(1u);wr(a,rd(a)&~bits);setmask(m);}
/* Stock 0x080086F4 (case_reset_context_transfer) */
void case_boot_sensor_irq_error(uint32_t descriptor)
{
    uint32_t hw=rd(descriptor);
    clear_locked(hw,0x120u);
    clear_locked(hw+8u,0x10000001u);
    if(rd(descriptor+108u)==1u)clear_locked(hw,16u);
    wr(descriptor+140u,32u);
    wr(descriptor+108u,0u);
    wr(descriptor+116u,0u);
}
void case_boot_sensor_irq_final(uint32_t descriptor){(void)descriptor;}
