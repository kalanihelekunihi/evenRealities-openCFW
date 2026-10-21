/* SPDX-License-Identifier: MIT
 * CASE 0x08006544 parser/notification callback for the input sensor stream.
 * RAM addresses are native layout addresses, not synthesized initial data.
 */
#include <stdint.h>
extern uint32_t case_boot_sensor_bind(uint32_t,uint32_t,uint32_t); /* 0x64ec */
extern uint32_t case_boot_sensor_finish_guard(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x63ec */
extern uint32_t case_boot_sensor_finish_probe(const uint8_t *); /* 0xbe74 */
extern int32_t case_boot_sensor_finish_signal(uint32_t,uint32_t); /* 0xa888 */
extern void case_boot_sensor_finish_reset(void); /* 0xa358 */
static uint8_t rd8(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void signal(uint32_t bits){(void)case_boot_sensor_finish_signal(rd32(0x200000f0u),bits);}
void case_boot_sensor_callback_finish(uint32_t descriptor)
{
    if(rd32(descriptor)!=0x40013800u)return;
    const uint32_t state=0x20000108u,buffer=0x20000974u,receiver=0x20000e24u;
    uint16_t count=rd16(state+2u);
    uint8_t byte=rd8(state);
    if(count!=0u){
        if(count<1200u){
            wr8(buffer+count,byte);count=(uint16_t)(count+1u);
            wr16(state+2u,count);wr8(state+1u,byte);
        }
        if(byte==10u && case_boot_sensor_finish_probe((const uint8_t *)(uintptr_t)buffer)!=0u){
            signal(8u);goto finish;
        }
    }else{
        if(byte=='Z'||byte=='D'||byte=='d'){
            wr8(buffer,byte);wr16(state+2u,1u);wr8(state+1u,byte);count=1u;
        }else goto bind;
    }
    if(rd8(buffer)!='Z'){
        if(count>1u && case_boot_sensor_finish_probe((const uint8_t *)(uintptr_t)buffer)==0u)
            goto reset;
        if(count<=60u)goto bind;
        goto reset;
    }
    if(count==1u)goto bind;
    if(count==2u){if(rd8(buffer+1u)==0xa5u)goto bind;goto reset;}
    if(count==3u){
        if(rd8(buffer+1u)!=0xa5u)goto reset;
        if(rd8(buffer+2u)==0x7fu||rd8(buffer+2u)==0xcfu)goto bind;
        goto reset;
    }
    if(count==4u){
        uint8_t format=rd8(buffer+2u);
        if(format==0xcfu)goto bind;
        if(format!=0x7fu)goto reset;
        uint32_t length=rd8(buffer+3u);
        if(case_boot_sensor_finish_guard(receiver,(const uint8_t *)(uintptr_t)(buffer+4u),length,10u)==3u)
            goto reset;
        count=(uint16_t)(count+length);wr16(state+2u,count);wr8(state+1u,rd8(buffer+count-1u));
        goto finish;
    }
    if(count==5u){
        uint8_t format=rd8(buffer+2u);
        if(format==0x7fu)goto bind;
        if(format!=0xcfu)goto reset;
        uint32_t length=(uint32_t)rd8(buffer+3u)|((uint32_t)rd8(buffer+4u)<<8);
        if(case_boot_sensor_finish_guard(receiver,(const uint8_t *)(uintptr_t)(buffer+5u),length,20u)==3u)
            goto reset;
        count=(uint16_t)(count+length);wr16(state+2u,count);wr8(state+1u,rd8(buffer+count-1u));
        goto finish;
    }
    if(rd8(buffer+2u)==0x7fu){
        uint32_t expected=(uint32_t)rd8(buffer+3u)+5u;
        if(count==expected){signal(8u);goto finish;}
        if(count>expected)goto reset;
    }else if(rd8(buffer+2u)==0xcfu){
        uint32_t expected=(uint32_t)rd8(buffer+3u)+((uint32_t)rd8(buffer+4u)<<8)+6u;
        if(count==expected){signal(8u);goto finish;}
        if(count>expected)goto reset;
    }else goto reset;
    goto finish;
reset:
    case_boot_sensor_finish_reset();
finish:
    if(rd16(state+2u)==1200u)case_boot_sensor_finish_reset();
bind:
    if(case_boot_sensor_bind(receiver,state,1u)!=0u)signal(64u);
}
