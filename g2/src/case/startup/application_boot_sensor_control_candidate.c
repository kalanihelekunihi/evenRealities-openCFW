/* SPDX-License-Identifier: MIT
 * Native CASE 0x5e2e, 0x5e6e, 0x5eb6 sensor control transactions.
 */
#include <stdint.h>
extern void case_boot_sensor_commit(uint32_t descriptor); /* 0x856c */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t busy(uint32_t d){return *(volatile uint8_t *)(uintptr_t)(d+132u);}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
/* Stock 0x08005E2E (case_guarded_controller_disable) */
uint32_t case_boot_sensor_start(uint32_t d)
{
    if(busy(d)==1u)return 2u;
    wr8(d+132u,1u);wr(d+136u,36u);
    uint32_t base=rd(d),control=rd(base);
    wr(base,control&~1u);
    wr(d+100u,0u);
    wr(base,control&~(1u<<29));
    wr(d+136u,32u);wr8(d+132u,0u);
    return 0u;
}
/* Stock 0x08005E6E (case_guarded_controller_field_mid) */
uint32_t case_boot_sensor_set_clock(uint32_t d,uint32_t clock)
{
    if(busy(d)==1u)return 2u;
    wr8(d+132u,1u);wr(d+136u,36u);
    uint32_t base=rd(d),control=rd(base);
    wr(base,control&~1u);
    wr(base+8u,(rd(base+8u)&~0x0e000000u)|clock);
    case_boot_sensor_commit(d);
    wr(base,control);wr(d+136u,32u);wr8(d+132u,0u);
    return 0u;
}
/* Stock 0x08005EB6 (case_guarded_controller_field_high) */
uint32_t case_boot_sensor_set_mode(uint32_t d,uint32_t mode)
{
    if(busy(d)==1u)return 2u;
    wr8(d+132u,1u);wr(d+136u,36u);
    uint32_t base=rd(d),control=rd(base);
    wr(base,control&~1u);
    wr(base+8u,(rd(base+8u)&0x1fffffffu)|mode);
    case_boot_sensor_commit(d);
    wr(base,control);wr(d+136u,32u);wr8(d+132u,0u);
    return 0u;
}
