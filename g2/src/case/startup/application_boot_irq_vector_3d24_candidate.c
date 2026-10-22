/* SPDX-License-Identifier: MIT
 * CASE USB edge IRQ vector at 0x08003d24. Child 0x3656 is a genuine
 * application reset operation and remains a separately typed contract.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format,...);
extern void case_boot_irq_hall_prepare(uint32_t mode);
extern uint32_t case_boot_irq_hall_state(void);
extern int32_t case_boot_sensor_finish_signal(uint32_t task,uint32_t bits);
extern void case_boot_irq_clear(uint32_t mask);
extern void case_boot_button_mode_reset(uint32_t active);
extern void case_init_boost_set(uint32_t enabled);
extern void case_boot_usb_reset_gls_box(void); /* stock 0x08003656 */
static uint8_t rd8(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x08003D24 (case_vector_irq_3d24) */
void case_vector_irq_3d24(void)
{
    const uint32_t s=0x2000087cu, quiet=0x200000bfu;
    wr8(s+3u,(uint8_t)((rd(0x40021810u)>>5u)&1u));
    if(rd8(quiet)==0u){
        (void)case_legacy_logger("USB int, hasUsb:%d",rd8(s+3u));
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
    if(rd8(s+3u)==0u){
        const uint32_t q=0x2000010cu, now=rd(s+8u), previous=rd(q);
        if((now-previous)<7u && previous!=0u && rd(q+4u)!=0u){
            if(rd8(quiet)==0u){
                (void)case_legacy_logger("Reset GLS and BOX, reason: USB.");
                (void)case_legacy_logger("\r\n");
            }
            case_boot_usb_reset_gls_box();
            (void)case_boot_sensor_finish_signal(rd(0x200000f0u),0x200u);
        }else{
            wr(q,rd(q+4u));
            wr(q+4u,now);
        }
    }
    case_init_boost_set(rd8(s+3u)==0u);
    case_boot_irq_clear(32u);
    if(rd8(quiet)==0u){
        (void)case_legacy_logger("USB int, send 0x13 soon.");
        (void)case_legacy_logger("\r\n");
    }
    if(rd8(s+49u)!=0u && rd16(s+56u)!=0u && rd8(s+51u)==0u)
        case_boot_button_mode_reset(1u);
    else wr(s+60u,0u);
    if(rd8(s+77u)!=0u && rd16(s+84u)!=0u && rd8(s+79u)==0u)
        case_boot_button_mode_reset(0u);
    else wr(s+88u,0u);
}
