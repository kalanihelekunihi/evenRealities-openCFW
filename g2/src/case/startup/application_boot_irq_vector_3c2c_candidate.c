/* SPDX-License-Identifier: MIT
 * CASE 0x08003c2c hall IRQ vector. The status and task notification paths
 * are complete C; 0x3848/0x2a5c are genuine native child bodies.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
extern void case_boot_irq_hall_prepare(uint32_t mode); /* 0x3848 */
extern uint32_t case_boot_irq_hall_state(void); /* 0x2a5c */
extern int32_t case_boot_sensor_finish_signal(uint32_t task,uint32_t bits); /* 0xa888 */
extern void case_boot_irq_clear(uint32_t mask); /* 0x4d04 */
extern void case_boot_button_mode_reset(uint32_t active); /* 0x3a00 */
static uint8_t rd8(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_vector_irq_3c2c(void)
{
    const uint32_t bus=0x40021800u,s=0x2000087cu,quiet=0x200000bfu;
    wr8(s+4u,(uint8_t)((rd(bus+12u)>>2u)&1u));
    wr8(0x20000104u,1u);
    if(rd8(quiet)==0u){
        (void)case_legacy_logger("hall int, isOpen:%d",rd8(s+4u));
        (void)case_legacy_logger("\r\n");
    }
    if(rd8(s+2u)==0u){
        case_boot_irq_hall_prepare(0u);
        wr8(s+2u,1u);
        (void)case_boot_sensor_finish_signal(rd(0x200000f0u),2u);
    }
    if(case_boot_irq_hall_state()!=0u)
        (void)case_boot_sensor_finish_signal(rd(0x200000f0u),0x1000u);
    else wr8(s+23u,0u);
    case_boot_irq_clear(4u);
    if(rd8(quiet)==0u){
        (void)case_legacy_logger("Hall int, send 0x13 soon.");
        (void)case_legacy_logger("\r\n");
    }
    if(rd8(s+49u)!=0u && rd16(s+56u)!=0u && rd8(s+51u)==0u)
        case_boot_button_mode_reset(1u);
    else wr(s+60u,0u);
    if(rd8(s+77u)!=0u && rd16(s+84u)!=0u && rd8(s+79u)==0u)
        case_boot_button_mode_reset(0u);
    else wr(s+88u,0u);
}
