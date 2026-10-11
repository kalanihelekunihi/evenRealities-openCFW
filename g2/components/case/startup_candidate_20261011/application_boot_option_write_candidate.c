/* SPDX-License-Identifier: MIT
 * Native CASE 0x4a6c option programming transaction with explicit wait child.
 */
#include <stdint.h>
extern uint32_t case_boot_option_status_a(void); /* 0x3ea8 */
extern uint32_t case_boot_option_status_b(void); /* 0x3ec0 */
extern uint32_t case_boot_option_wait(uint32_t ticks); /* 0x3f6c */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void program(uint32_t clear,uint32_t first,uint32_t second) /* 0x3ed4 */
{wr(0x40022020u,(rd(0x40022020u)&~(clear|0xffu))|first|second);}
uint32_t case_boot_option_write(const uint32_t *words)
{
    volatile uint8_t *busy=(volatile uint8_t *)(uintptr_t)0x20000f98u;
    if(*busy==1u)return 2u;
    *busy=1u;
    wr(0x20000f9cu,0u);
    uint32_t control=words[0];
    if((control&1u)!=0u){
        uint32_t register_address;
        if(words[1]==1u)register_address=0x4002202cu;
        else if(words[1]==4u)register_address=0x4002204cu;
        else if(words[1]==8u)register_address=0x40022050u;
        else register_address=0x40022030u;
        wr(register_address,(words[3]<<16)|words[2]);
    }
    if(((control>>1)&3u)==3u)program(words[5],words[6],words[4]);
    else if((control&2u)!=0u){uint32_t status=case_boot_option_status_b();program(status,status,words[4]);}
    else if((control&4u)!=0u)program(words[5],words[6],case_boot_option_status_a());
    uint32_t result=case_boot_option_wait(1000u);
    if(result==0u){
        wr(0x40022014u,rd(0x40022014u)|0x20000u);
        result=case_boot_option_wait(1000u);
        wr(0x40022014u,rd(0x40022014u)&~0x20000u);
    }
    *busy=0u;
    return result;
}
