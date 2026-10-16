/* SPDX-License-Identifier: MIT */
/* Reconstruction from locked Apollo firmware: callback4b4a98..4b4ab2,
 * registration slice4b49a8..4b49b6, ISR4b80be..4b80ea.
 * GPIO leaf APIs retain their pinned upstream BSD3 attribution separately. */
#include "radio_gpio.h"
#include "../ambiq_gpio/ambiq_gpio.h"
#include "../ambiq_mspi/ambiq_interrupt_mask.h"
_Static_assert(sizeof(void *)==4,"stock ARM32 consumer");
#define REG32(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_radio_gpio_callback(void *argument)
{
    (void)argument;
    REG32(0x20074640u) = REG32(0x20074640u) + 1u;
    opencfw_radio_scheduler_event(*(volatile uint8_t *)(uintptr_t)0x20074fcbu,1u);
}
uint32_t opencfw_radio_gpio_register(void)
{
    return am_hal_gpio_interrupt_register(AM_HAL_GPIO_INT_CHANNEL_0,117u,
                                         opencfw_radio_gpio_callback,(void *)0);
}
void GPIO0_607F_IRQHandler(void)
{
    /* Preserve the unused seven-bank snapshot and its MMIO read order.
     * This reconstructs only channel0/enabledOnly=false of stock4812f6,
     * not the general all-channel snapshot API. */
    volatile uint32_t snapshot[7];
    uint32_t prior=am_hal_interrupt_master_disable();
    for(uint32_t bank=0;bank<7;bank++)
        snapshot[bank]=REG32(0x40010534u+bank*0x10u);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    (void)snapshot;
    uint32_t mask;
    (void)am_hal_gpio_interrupt_irq_status_get(59u,false,&mask);
    (void)am_hal_gpio_interrupt_irq_clear(59u,mask);
    (void)am_hal_gpio_interrupt_service(59u,mask);
}

/* Specialized stock channel0/INDV_ENABLE-DISABLE/pin117 path through4810b0.
 * This is not a replacement for the general GPIO interrupt-control API. */
void opencfw_radio_gpio_enable(void)
{
    uint32_t prior=am_hal_interrupt_master_disable();
    REG32(0x40010560u) |= (1u<<21);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
}
void opencfw_radio_gpio_disable(void)
{
    uint32_t prior=am_hal_interrupt_master_disable();
    REG32(0x40010560u) &= ~(1u<<21);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
}
void opencfw_radio_gpio_irq_setup(void)
{
    (void)opencfw_radio_gpio_register();
    opencfw_radio_gpio_enable();
    *(volatile uint8_t *)(uintptr_t)0xe000e43bu=0x40u;
    REG32(0xe000e104u)=1u<<27;
}
