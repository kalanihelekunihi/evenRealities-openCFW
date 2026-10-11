/* Fixture-only prefix: only invalid mapping and already-on/off return paths.
 * The sentinel return for other states forbids use as a production provider. */
#include <stdint.h>
#include "../../components/foundation/power_domain/power_domain.h"
#define UNREACHED 0xfeedbeefu
extern uint32_t stock_save_irq(void);
extern uint32_t audio_wait5(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t power_enable_prefix_probe(uint32_t peripheral)
{
    opencfw_power_domain_descriptor_t p;
    uint32_t status = opencfw_power_domain_descriptor(&p, (uint8_t)peripheral);
    if (status) return status;
    if (*(volatile uint32_t *)(uintptr_t)p.enable_register & p.enable_mask) return 0;
    /* Authenticated stock compares low-byte peripheral 0x17, unlike the
       pinned upstream enum where CRYPTO has another index. */
    if ((uint8_t)peripheral == 0x17u &&
        !(*(volatile uint32_t *)0x40021008u & (1u << 27))) return 1;
    /* Pinned SPOT wrapper: null Tempco hook is a successful no-op; the
       selected ordinary domain reports its requested status to SPOT. */
    volatile uint32_t *spot = (volatile uint32_t *)0x20073270u;
    if (spot[3]) ((uint32_t (*)(void))(uintptr_t)spot[3])();
    if (p.enable_mask && (uint8_t)peripheral < 30u) {
        if (spot[1])
            (void)((uint32_t (*)(uint32_t,uint32_t,void *))(uintptr_t)spot[1])(3u,1u,&p.status_mask);
    }
    if ((uint8_t)peripheral >= 30u && (p.enable_mask & 0x4c4u) && spot[1])
        (void)((uint32_t (*)(uint32_t,uint32_t,void *))(uintptr_t)spot[1])(4u,1u,&p.status_mask);
    uint32_t saved = stock_save_irq();
    *(volatile uint32_t *)(uintptr_t)p.enable_register |= p.enable_mask;
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    if (spot[4]) (void)((uint32_t (*)(void))(uintptr_t)spot[4])();
    if ((uint8_t)peripheral == 0u || (uint8_t)peripheral == 30u) {
        status = audio_wait5(5u,p.status_register,p.status_mask,p.status_mask,1u);
        if (status) return status;
        return (*(volatile uint32_t *)(uintptr_t)p.status_register & p.status_mask) ? 0u : 1u;
    }
    return UNREACHED;
}
uint32_t power_disable_prefix_probe(uint32_t peripheral)
{
    opencfw_power_domain_descriptor_t p;
    uint32_t status = opencfw_power_domain_descriptor(&p, (uint8_t)peripheral);
    if (status) return status;
    if (!(*(volatile uint32_t *)(uintptr_t)p.enable_register & p.enable_mask)) return 0;
    if ((uint8_t)peripheral == 0x1du &&
        ((*(volatile uint32_t *)0x4002000cu & 0xffu) < 0x22u) &&
        (*(volatile uint32_t *)0x40021008u & (1u << 21))) return 3u;
    if ((uint8_t)peripheral == 0u || (uint8_t)peripheral == 3u || (uint8_t)peripheral == 30u) {
        volatile uint32_t *spot = (volatile uint32_t *)0x20073270u;
        if (spot[3]) (void)((uint32_t (*)(void))(uintptr_t)spot[3])();
        uint32_t saved = stock_save_irq();
        *(volatile uint32_t *)(uintptr_t)p.enable_register &= ~p.enable_mask;
        __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
        if ((uint8_t)peripheral == 3u) {
            uint32_t remaining = *(volatile uint32_t *)(uintptr_t)p.enable_register;
            if ((remaining & 0x1eu) && !(remaining & p.enable_mask)) {
                if (spot[4]) (void)((uint32_t (*)(void))(uintptr_t)spot[4])();
                return 0;
            }
        }
        status = audio_wait5(5u,p.status_register,p.status_mask,p.status_mask,0u);
        if (!status && p.enable_mask && spot[1])
            (void)((uint32_t (*)(uint32_t,uint32_t,void *))(uintptr_t)spot[1])((uint8_t)peripheral >= 30u ? 4u : 3u,0u,&p.status_mask);
        if (spot[4]) (void)((uint32_t (*)(void))(uintptr_t)spot[4])();
        return status;
    }
    return UNREACHED;
}
