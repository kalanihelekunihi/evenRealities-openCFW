/* SPDX-License-Identifier: MIT. Reconstructed locked 0x42c988..0x42cc34.
 * CQ adapter calls remain explicit dependencies; peripheral effects are MMIO. */
#include "context_claim.h"
#include "../clock_manager/clock_manager.h"
extern uint32_t opencfw_bl_mspi_mode_enter(uint32_t selector);
extern uint32_t opencfw_bl_mspi_mode_leave(uint32_t selector);
extern uint32_t opencfw_boot_iom_cq_enable(void *handle);
extern uint32_t opencfw_boot_iom_cq_disable(void *handle);
extern uint32_t opencfw_hal_status_poll(uint32_t, uintptr_t, uint32_t, uint32_t, uint32_t);
#define WORD(h,o) (*(volatile uint32_t *)((uintptr_t)(h)+(o)))
#define BYTE(h,o) (*(volatile uint8_t *)((uintptr_t)(h)+(o)))
#define REG(h,o) (*(volatile uint32_t *)(0x40050000u + (h)->module * 0x1000u + (o)))
uint32_t opencfw_boot_context_transaction(struct opencfw_iom_context *h,
                                         uint32_t command, uint32_t retain)
{
    if (h == 0 || (h->flags & 0x01ffffffu) != 0x01123456u) return 2u;
    command = (uint8_t)command;
    retain = (uint8_t)retain;
    if (command == 0u) {
        if (retain && !BYTE(h,0x868u)) return 7u;
        (void)opencfw_bl_mspi_mode_enter((uint8_t)(h->module+3u));
        if (retain) {
            REG(h,0x104u)=WORD(h,0x86cu);
            REG(h,0x118u)=WORD(h,0x874u);
            REG(h,0x22cu)=WORD(h,0x880u);
            REG(h,0x234u)=WORD(h,0x884u);
            REG(h,0x23cu)=WORD(h,0x888u);
            REG(h,0x240u)=WORD(h,0x88cu);
            REG(h,0x244u)=WORD(h,0x890u);
            REG(h,0x280u)=WORD(h,0x894u);
            REG(h,0x2c0u)=WORD(h,0x898u);
            REG(h,0x200u)=WORD(h,0x89cu);
            REG(h,0x210u)=WORD(h,0x870u);
            REG(h,0x228u)=WORD(h,0x87cu)&~1u;
            REG(h,0x11cu)=WORD(h,0x878u);
            if (BYTE(h,0x87cu)&1u) (void)opencfw_boot_iom_cq_enable(h);
            if (h->flags & 0x02000000u)
                (void)opencfw_hal_status_poll(1000u,
                    0x40050248u+h->module*0x1000u,6u,4u,1u);
            BYTE(h,0x868u)=0u;
        }
        return clock_request(4u,(uint8_t)(h->module+3u));
    }
    if (command != 1u && command != 2u) return 6u;
    if ((h->flags & 0x02000000u) &&
        ((REG(h,0x248u)&6u)!=4u || WORD(h,0x24u)!=0u)) return 3u;
    if (retain) {
        WORD(h,0x86cu)=REG(h,0x104u);
        WORD(h,0x874u)=REG(h,0x118u);
        WORD(h,0x878u)=REG(h,0x11cu);
        WORD(h,0x87cu)=REG(h,0x228u);
        WORD(h,0x880u)=REG(h,0x22cu);
        WORD(h,0x884u)=REG(h,0x234u);
        WORD(h,0x888u)=REG(h,0x23cu);
        WORD(h,0x88cu)=REG(h,0x240u);
        WORD(h,0x890u)=REG(h,0x244u);
        WORD(h,0x894u)=REG(h,0x280u);
        WORD(h,0x898u)=REG(h,0x2c0u);
        WORD(h,0x89cu)=REG(h,0x200u);
        WORD(h,0x870u)=REG(h,0x210u);
        if (REG(h,0x228u)&1u) (void)opencfw_boot_iom_cq_disable(h);
        BYTE(h,0x868u)=1u;
    }
    REG(h,0x11cu)&=~1u;
    REG(h,0x11cu)&=~0x10u;
    (void)opencfw_bl_mspi_mode_leave((uint8_t)(h->module+3u));
    return clock_release(4u,(uint8_t)(h->module+3u));
}
