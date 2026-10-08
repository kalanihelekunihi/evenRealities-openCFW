/* SPDX-License-Identifier: MIT
 * Request 26 clock-selection path from stock 0x4258ec..0x425c5a. Clock
 * request/release, clockgen, and XIP-delay helpers are separately recovered
 * providers. MMIO is volatile hardware state; fixture MMIO is synthetic.
 */
#include "control_request_clock.h"
#include "../nor_mspi_power/device_configure.h"
#include <stdint.h>

#define MSPI_BASE UINT32_C(0x40060000)

extern uint32_t opencfw_bl_mspi_clockgen_control(uint32_t module,
    uint32_t enable,uint32_t configure,uint32_t source);
extern uint32_t clock_release(uint32_t source,uint32_t user);
extern uint32_t clock_request(uint32_t source,uint32_t user);
extern void opencfw_bl_mspi_get_xip_off_min_delay(uint32_t *handle);

static volatile uint32_t *reg(uint32_t module,uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)(MSPI_BASE+(module<<12)+offset);
}

static uint32_t field(uint32_t module,uint32_t offset,uint32_t shift,
                      uint32_t width,uint32_t value)
{
    volatile uint32_t *const p=reg(module,offset);
    const uint32_t mask=((UINT32_C(1)<<width)-1u)<<shift;
    *p=(*p&~mask)|((value<<shift)&mask);
    return *p;
}

static uint32_t divisor(uint8_t frequency)
{
    if(frequency<=3u)return 0x20u;
    if(frequency<=5u)return 0x18u;
    if(frequency<=7u)return 0x10u;
    if(frequency<=9u)return 0x0cu;
    if(frequency<=11u)return 8u;
    if(frequency<=13u)return 6u;
    if(frequency<=15u)return 4u;
    if(frequency<=17u)return 3u;
    if(frequency<=19u)return 2u;
    return 1u;
}

uint32_t opencfw_hal_mspi_control_clock_request(uint32_t handle_address,
                                               void *config)
{
    uint32_t *const handle=(uint32_t *)(uintptr_t)handle_address;
    const uint32_t module=handle[1];
    const uint8_t frequency=*(const volatile uint8_t *)config;
    uint32_t source;
    uint32_t status;

    if((module==1u||module==2u)&&frequency>=21u&&frequency<=23u)
        return 5u;

    (void)opencfw_bl_mspi_clockgen_control(module,0u,0u,0u);
    source=(frequency>=3u&&frequency<=23u&&(frequency&1u)!=0u)?5u:4u;
    if(*(volatile uint8_t *)((uintptr_t)handle+0x8c9u)!=(uint8_t)source){
        status=clock_release(*(volatile uint8_t *)((uintptr_t)handle+0x8c9u),module+0x10u);
        if(status!=0u)return status;
        status=clock_request(source,module+0x10u);
        if(status!=0u)return status;
    }
    *(volatile uint8_t *)((uintptr_t)handle+0x8c9u)=(uint8_t)source;

    if(frequency>=1u&&frequency<=23u){
        uint32_t io_source;
        if(frequency==1u)io_source=7u;
        else if((frequency&1u)==0u)io_source=8u;
        else io_source=10u;
        (void)opencfw_bl_mspi_clockgen_control(module,1u,1u,io_source);
        if(frequency==22u||frequency==23u)
            *reg(module,0x8cu)|=0x40000000u;
        else
            *reg(module,0x8cu)&=~0x40000000u;
    }else{
        return 5u;
    }

    if(frequency>=20u)
        (void)field(module,0x84u,16u,6u,1u);
    else
        (void)field(module,0x84u,16u,6u,divisor(frequency));
    if(frequency>=20u)
        *reg(module,0x84u)|=0x01000000u;
    else
        *reg(module,0x84u)&=~0x01000000u;
    *reg(module,0x84u)&=~0x00800000u;
    *reg(module,0x84u)&=~0x00400000u;

    if(handle[6]!=0u){
        *reg(module,0x114u)=0x20u;
        if(frequency>=1u&&frequency<=17u)
            (void)field(module,0x118u,0u,5u,8u);
        else if(frequency>=18u&&frequency<=23u)
            (void)field(module,0x118u,0u,5u,12u);
        else
            return 5u;
        (void)field(module,0x20u,8u,6u,0x1eu);
        (void)field(module,0x118u,8u,5u,8u);
    }

    *(volatile uint8_t *)((uintptr_t)handle+0xcu)=frequency;
    opencfw_bl_mspi_get_xip_off_min_delay(handle);
    return 0u;
}
