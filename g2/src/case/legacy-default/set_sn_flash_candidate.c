/* SPDX-License-Identifier: MIT
 * Full fixed-image 0x08003664 eight-byte serial-number flash update.
 * The bytes are caller supplied; controller effects are sourced lower bodies.
 */
#include <stdint.h>
extern uint32_t case_binary_5e_flash_mode(void);
extern uint32_t case_binary_5e_flash_init(void);
extern uint32_t case_binary_5e_flash_read(void *config,uint32_t *error);
extern uint32_t case_binary_5e_wait(uint32_t ticks);
extern uint32_t case_binary_5e_flash_program(uint32_t operation,uint32_t address,uint32_t low,uint32_t high);
extern uint32_t case_binary_5e_flash_finish(void);
extern uint32_t case_legacy_logger(const char *format,...);
static uint32_t pack(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
/* Stock 0x08003664 (case_legacy_set_sn) */
uint32_t case_legacy_set_sn(const uint8_t *bytes)
{
    volatile uint32_t *cfg=(volatile uint32_t *)(uintptr_t)0x200001a4u;
    cfg[0]=2u;
    cfg[1]=case_binary_5e_flash_mode()==1u?4u:0x8000u;
    cfg[2]=0x7fu;cfg[3]=1u;
    (void)case_binary_5e_flash_init();
    uint32_t error=0u;
    uint32_t tries=0u;
    do{
        if(case_binary_5e_flash_read((void *)(uintptr_t)0x200001a4u,&error)==0u)break;
        (void)case_binary_5e_wait(10u);
        ++tries;
    }while(tries<3u);
    if(tries==3u){
        if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u)
            (void)case_legacy_logger("fail to erase. err:0x%x",error);
    }else if(case_binary_5e_flash_program(1u,0x0803f800u,pack(bytes+4u),pack(bytes))!=0u){
        if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u)
            (void)case_legacy_logger("fail to program.");
    }else return case_binary_5e_flash_finish();
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u)
        (void)case_legacy_logger("\r\n");
    return case_binary_5e_flash_finish();
}
