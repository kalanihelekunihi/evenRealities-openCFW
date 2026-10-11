/* SPDX-License-Identifier: MIT
 * CASE 0x08003a00 mode reset and 0x08003a84 button/battery IRQ refresh.
 * The 0x9ebc sampler is source-owned as case_init_read_product_byte; all RAM
 * state and literals below are read from the native branch graph.
 */
#include <stdint.h>
extern int32_t case_init_read_product_byte(uint32_t *out); /* 0x9ebc */
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
extern uint32_t case_init_pmic_write(uint32_t reg,uint32_t value); /* 0x39c8 */
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static uint8_t rd8(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
void case_boot_button_mode_reset(uint32_t active)
{
    const uint32_t s=0x2000087cu;
    if(active!=0u){
        wr8(s+52u,0u);wr(s+60u,0u);wr(s+72u,0u);wr16(s+56u,0u);
        wr8(s+49u,0u);wr8(s+18u,1u);
    }else{
        wr8(s+80u,0u);wr(s+88u,0u);wr(s+100u,0u);wr16(s+84u,0u);
        wr8(s+77u,0u);wr8(s+19u,1u);
    }
}
void case_boot_irq_button_refresh(void)
{
    uint32_t sampled;
    if(case_init_read_product_byte(&sampled)==0){
        const uint32_t s=0x2000087cu,quiet=0x200000b8u;
        uint8_t previous=rd8(s+1u);
        if(rd8(s+3u)==0u || (int32_t)previous<(int32_t)sampled){
            if(rd8(quiet+7u)==0u){
                (void)case_legacy_logger("Bat change: %d -> %d",previous,sampled);
                (void)case_legacy_logger("\r\n");
            }
            wr8(s+1u,(uint8_t)sampled);
            if(rd8(quiet+7u)==0u){
                (void)case_legacy_logger("Bat change, send 0x13 soon.");
                (void)case_legacy_logger("\r\n");
            }
            if(rd8(s+49u)!=0u && rd16(s+56u)!=0u && rd8(s+51u)==0u)
                case_boot_button_mode_reset(1u);
            else wr(s+60u,0u);
            if(rd8(s+77u)!=0u && rd16(s+84u)!=0u && rd8(s+79u)==0u)
                case_boot_button_mode_reset(0u);
            else wr(s+88u,0u);
        }else if(rd8(quiet+7u)==0u){
            (void)case_legacy_logger("Bat change(not used): %d -> %d",previous,sampled);
            (void)case_legacy_logger("\r\n");
        }
    }
    (void)case_init_pmic_write(10u,64u);
}
