/* SPDX-License-Identifier: MIT. Locked 42cc34 configuration and42c538 enable. */
#include "context_claim.h"
extern uint64_t opencfw_boot_iom_clock_config(uint32_t hz, uint32_t phase);
extern uint32_t opencfw_boot_iom_cq_initialize(void *, uint32_t, uint32_t);
extern uint32_t opencfw_hal_status_poll(uint32_t, uintptr_t, uint32_t, uint32_t, uint32_t);
#define WORD(h,o) (*(volatile uint32_t *)((uintptr_t)(h)+(o)))
#define BYTE(h,o) (*(volatile uint8_t *)((uintptr_t)(h)+(o)))
#define REG(h,o) (*(volatile uint32_t *)(0x40050000u+(h)->module*0x1000u+(o)))

uint32_t opencfw_boot_context_configure(struct opencfw_iom_context *h,
                                       const struct opencfw_iom_instance_config *config)
{
    if (!h || (h->flags&0x01ffffffu)!=0x01123456u) return 2u;
    if (!config || h->module>=8u) return 6u;
    if (h->flags&0x02000000u) return 7u;
    BYTE(h,8u)=config->interface;
    REG(h,0x104u)=0x1010u;
    uint32_t clock;
    if (config->interface==0u) {
        if (config->spi_mode>=4u || config->clock_hz>=48000001u) return 6u;
        clock=(uint32_t)opencfw_boot_iom_clock_config(config->clock_hz,
                                                    (config->spi_mode>>1)&1u);
        REG(h,0x280u)=config->spi_mode&3u;
    } else if (config->interface==1u) {
        if (config->clock_hz==100000u) {clock=0x773b2301u;REG(h,0x2c0u)=0x3f070u;}
        else if (config->clock_hz==400000u) {clock=0x1d0e2301u;REG(h,0x2c0u)=0x3f270u;}
        else if (config->clock_hz==1000000u) {clock=0x0b052301u;REG(h,0x2c0u)=0x23040u;}
        else return 6u;
    } else return 5u;
    REG(h,0x118u)=clock|1u;
    /* Cortex-M UDIV with a zero divisor yields0 when DIV_0_TRP is clear.
     * Preserve that locked-instruction case rather than C division UB. */
    WORD(h,0x864u)=config->clock_hz?1000000u/config->clock_hz:0u;
    WORD(h,0x860u)=1000u;
    WORD(h,0xcu)=config->queue_buffer;
    WORD(h,0x10u)=config->queue_words;
    if (WORD(h,0xcu)!=0u) {
        BYTE(h,0x8a4u)=((WORD(h,0xcu)+(WORD(h,0x10u)<<2))<0x20080000u);
        WORD(h,0x858u)=((WORD(h,0x10u)-8u)<<2)/96u;
        if (WORD(h,0x858u)>=257u) WORD(h,0x858u)=256u;
    }
    for (uint32_t i=0;i<4u;++i) BYTE(h,0x8a0u+i)=0u;
    return 0u;
}
__attribute__((noinline)) uint32_t opencfw_boot_iom_select_interface(uint32_t module,uint32_t interface)
{
    volatile uint32_t *const reg=(volatile uint32_t *)(0x4005011cu+module*0x1000u);
    if (((*reg>>1)&7u)==interface) {*reg=1u;return 1u;}
    if (((*reg>>5)&7u)==interface) {*reg=0x10u;return 1u;}
    return 0u;
}
uint32_t opencfw_boot_context_enable(struct opencfw_iom_context *h)
{
    if (!h || (h->flags&0x01ffffffu)!=0x01123456u) return 2u;
    if (h->flags&0x02000000u) return 0u;
    if (!opencfw_boot_iom_select_interface(h->module,BYTE(h,8u)!=0u)) return 9u;
    uint32_t status=0u;
    if (WORD(h,0xcu)!=0u) {
        WORD(h,0x24u)=0u;
        WORD(h,0x1cu)=0u;
        REG(h,0x238u)=0x800040u;
        WORD(h,0x854u)=0u;
        BYTE(h,0x83cu)=0u;
        WORD(h,0x838u)=0u;
        WORD(h,0x844u)=0u;
        WORD(h,0x840u)=0u;
        BYTE(h,0x82cu)=0u;
        WORD(h,0x830u)=0u;
        BYTE(h,0x82du)=1u;
        status=opencfw_boot_iom_cq_initialize(h,WORD(h,0x10u),WORD(h,0xcu));
        REG(h,0x210u)=2u;
    }
    if (status!=0u) return status;
    status=opencfw_hal_status_poll(1000u,0x40050248u+h->module*0x1000u,6u,4u,1u);
    if (!status) h->flags|=0x02000000u;
    else {REG(h,0x11cu)&=~1u;REG(h,0x11cu)&=~0x10u;}
    return status;
}
