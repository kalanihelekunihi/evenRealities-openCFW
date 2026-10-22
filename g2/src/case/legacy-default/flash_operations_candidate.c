/* SPDX-License-Identifier: MIT
 * Stock CASE flash status/erase/program wrappers, translated from the
 * retained instruction-grounded pseudocode. Final erase/program leaves and
 * physical flash-controller state remain explicit external contracts.
 */
#include <stdint.h>

extern uint32_t case_tick_word2(void); /* 0x08004eac */
extern void case_flash_erase_mode4(uint32_t address); /* 0x08003e94 */
extern void case_flash_erase_page(uint32_t address,uint32_t page); /* 0x08003eec */
extern void case_flash_program_doubleword(uint32_t address,uint32_t retained_r1,
                                          uint32_t low,uint32_t high); /* 0x08003f1c */
extern void case_flash_copy_operation(uint32_t address,uint32_t source); /* 0x08003f38 */

/* Stock 0x08003F6C (case_wait_serial_idle) */
uint32_t case_flash_status_wait(uint32_t timeout) /* 0x08003f6c */
{
    volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)0x40022010u;
    volatile uint32_t *error_word=(volatile uint32_t *)(uintptr_t)0x20000f9cu;
    uint32_t deadline=case_tick_word2()+timeout;
    while((*status&0x30000u)!=0u) {
        if(case_tick_word2()>=deadline) return 3u;
    }
    uint32_t errors=*status&0x83fau;
    *status=0x883fbu;
    if(errors!=0u) {
        *error_word=errors;
        return 1u;
    }
    deadline=case_tick_word2()+timeout;
    while((*status&0x40000u)!=0u) {
        if(case_tick_word2()>=deadline) return 3u;
    }
    return 0u;
}

/* Stock 0x0800497C (case_run_controller_range) */
uint32_t case_binary_5e_flash_read(void *configuration,uint32_t *error_page) /* 0x0800497c */
{
    const uint32_t *cfg=(const uint32_t *)configuration;
    volatile uint8_t *lock=(volatile uint8_t *)(uintptr_t)0x20000f98u;
    volatile uint32_t *error=(volatile uint32_t *)(uintptr_t)0x20000f9cu;
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40022014u;
    if(*lock==1u) return 2u;
    *lock=1u;
    *error=0u;
    uint32_t result=case_flash_status_wait(1000u);
    if(result==0u) {
        if(cfg[0]==4u) {
            case_flash_erase_mode4(cfg[1]);
            result=case_flash_status_wait(1000u);
        } else {
            *error_page=UINT32_MAX;
            uint32_t limit=cfg[2]+cfg[3];
            for(uint32_t page=cfg[2];page<limit;++page) {
                case_flash_erase_page(cfg[1],page);
                result=case_flash_status_wait(1000u);
                if(result!=0u) {*error_page=page;break;}
            }
            *control&=~2u;
        }
    }
    *lock=0u;
    return result;
}

/* Stock 0x08004B94 (case_copy_controller_words) */
uint32_t case_binary_5e_flash_program(uint32_t operation,uint32_t address,
                                      uint32_t arg2,uint32_t arg3) /* 0x08004b94 */
{
    volatile uint8_t *lock=(volatile uint8_t *)(uintptr_t)0x20000f98u;
    volatile uint32_t *error=(volatile uint32_t *)(uintptr_t)0x20000f9cu;
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40022014u;
    if(*lock==1u) return 2u;
    *lock=1u;
    *error=0u;
    uint32_t result=case_flash_status_wait(1000u);
    if(result==0u) {
        if(operation==1u) case_flash_program_doubleword(address,address,arg2,arg3);
        else case_flash_copy_operation(address,arg2);
        result=case_flash_status_wait(1000u);
        *control&=~operation;
    }
    *lock=0u;
    return result;
}
