#include "../../../../components/bootloader/nor_mspi_power/power_control.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static uint32_t regs[2][0x300 / 4];
static uint32_t request_status, release_status;
static uint32_t mode_enter_calls, mode_leave_calls, delay_calls;
static uint32_t cq_disable_calls, cq_enable_calls, irq_disable_calls;
static uint32_t last_delay, last_user, last_clock, last_mask;

static uint32_t mode_enter(uint8_t user) { ++mode_enter_calls; last_user=user; return 0; }
static uint32_t mode_leave(uint8_t user) { ++mode_leave_calls; last_user=user; return 0; }
static uint32_t clock_request(uint8_t clock, uint8_t user) {
    last_clock=clock; last_user=user; return request_status;
}
static uint32_t clock_release_all(uint8_t user) { last_user=user; return release_status; }
static void clockgen(uint32_t module, uint8_t en, uint8_t cfg, uint8_t src) {
    (void)module; (void)en; (void)cfg; (void)src;
}
static uint32_t cq_disable(uint32_t *handle) { (void)handle; ++cq_disable_calls; return 0; }
static void cq_enable(uint32_t *handle) { (void)handle; ++cq_enable_calls; }
static uint32_t irq_disable(uint32_t *handle, uint32_t mask) {
    (void)handle; ++irq_disable_calls; last_mask=mask; return 0;
}
static void delay_us(uint32_t value) { ++delay_calls; last_delay=value; }
static uint32_t mmio_read(uint32_t module, uint16_t offset) {
    return regs[module][offset / 4u];
}
static void mmio_write(uint32_t module, uint16_t offset, uint32_t value) {
    regs[module][offset / 4u]=value;
}
static const opencfw_mspi_power_ops_t ops = {
    mode_enter, mode_leave, clock_request, clock_release_all, clockgen,
    cq_disable, cq_enable, irq_disable, delay_us, mmio_read, mmio_write
};

static void reset(void) {
    memset(regs, 0, sizeof(regs));
    request_status=release_status=0;
    mode_enter_calls=mode_leave_calls=delay_calls=0;
    cq_disable_calls=cq_enable_calls=irq_disable_calls=0;
    last_delay=last_user=last_clock=last_mask=0;
}

static void init_handle(uint32_t *h) {
    memset(h, 0, 0x8d0);
    h[0]=0x01bebebeu;
    h[1]=1u;
}

int main(void) {
    uint32_t h[0x8d0 / 4];
    reset(); init_handle(h);
    assert(opencfw_hal_mspi_power_control(NULL, 1, 0, &ops)==2);
    h[0]=0;
    assert(opencfw_hal_mspi_power_control(h, 1, 0, &ops)==2);

    reset(); init_handle(h);
    assert(opencfw_hal_mspi_power_control(h, 3, 0, &ops)==6);
    h[0x210]=1;
    assert(opencfw_hal_mspi_power_control(h, 1, 0, &ops)==3);
    h[0x210]=0; h[8]=1;
    assert(opencfw_hal_mspi_power_control(h, 2, 0, &ops)==3);

    reset(); init_handle(h);
    ((uint8_t *)h)[0x860]=1;
    h[0x219]=0; h[0x228]=0x80000001u; h[0x233]=37;
    regs[1][0x90/4]=1u;
    regs[1][0x2a0/4]=0x80000001u;
    for (uint32_t i=0;i<0x300/4;i++) regs[1][i]=0x51000000u+i;
    regs[1][0x90/4]=1u;
    regs[1][0x2a0/4]=1u;
    assert(opencfw_hal_mspi_power_control(h, 1, 1, &ops)==0);
    assert(((uint8_t *)h)[0x860]==1);
    assert(h[0x219]==regs[1][0x80/4]);
    assert(h[0x228]==1u);
    assert(cq_disable_calls==1 && irq_disable_calls==1);
    assert(last_mask==0x1fffu && delay_calls==1 && last_delay==37);
    assert(mode_leave_calls==1 && last_user==0x11u);

    /* A failed clock request short-circuits before register restore/enable. */
    reset(); init_handle(h);
    ((uint8_t *)h)[0x860]=1; ((uint8_t *)h)[0x8c9]=3;
    request_status=9;
    assert(opencfw_hal_mspi_power_control(h, 0, 1, &ops)==9);
    assert(mode_enter_calls==1 && cq_enable_calls==0);

    /* Save path followed by restore path exercises the full state map. */
    reset(); init_handle(h);
    ((uint8_t *)h)[0x8c9]=4;
    for (uint32_t i=0;i<0x300/4;i++) regs[1][i]=0xA5000000u+i;
    regs[1][0x2a0/4]=1u;
    assert(opencfw_hal_mspi_power_control(h, 2, 1, &ops)==0);
    assert(((uint8_t *)h)[0x860]==1);
    assert(opencfw_hal_mspi_power_control(h, 0, 1, &ops)==0);
    assert(((uint8_t *)h)[0x860]==0);
    assert(regs[1][0x2a0/4]==0u); /* CQCFG with enable bit cleared */
    assert(cq_enable_calls==1 && mode_enter_calls==1);
    assert(last_clock==4u && last_user==0x11u);

    /* Invalid save state and release failure are distinct return paths. */
    reset(); init_handle(h);
    assert(opencfw_hal_mspi_power_control(h, 0, 1, &ops)==7);
    reset(); init_handle(h);
    release_status=5;
    assert(opencfw_hal_mspi_power_control(h, 1, 0, &ops)==5);

    puts("MSPI power-control source checks: 23 assertions passed");
    return 0;
}
