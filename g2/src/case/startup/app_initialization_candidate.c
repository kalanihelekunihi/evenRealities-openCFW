#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Experimental full control-flow reduction of stock 0x08002fc8. Peripheral
 * actions and stock format strings remain typed product contracts. This
 * body is not selected as a production initializer without a full oracle.
 */
#include <stdint.h>
extern uint32_t case_init_id0(void);                 /* 0x08004ed0 */
extern uint32_t case_init_id1(void);                 /* 0x08004ec4 */
extern uint32_t case_init_id2(void);                 /* 0x08004eb8 */
extern void case_init_log(uint32_t message,uint32_t arg0,uint32_t arg1,uint32_t arg2);
extern uint32_t case_init_pin_read(uint32_t base,uint32_t mask); /* 0x08004e94 */
extern void case_init_sensor_prepare(void);         /* 0x08003a30 */
extern void case_init_selfcheck_read(uint32_t selector,uint8_t *out,uint32_t count); /* 0x080035b8 */
extern void case_init_wait(uint32_t ticks);          /* 0x08004958 */
extern void case_init_pmic_prepare(void);            /* 0x08009df4 */
extern void case_init_pmic_read(uint32_t address,uint8_t *out,uint32_t count); /* 0x080035d4 */
extern uint32_t case_init_pmic_reset(uint32_t address,uint32_t value); /* 0x080039e4 */
extern void case_init_power_set(uint32_t value);    /* 0x08002c8e */
extern void case_init_wake_mask(uint32_t value);    /* 0x08005094 */
extern void case_init_wake_config(uint32_t value);  /* 0x080050a8 */
extern void case_init_wake_clock(void);              /* 0x080050c4 */
extern void case_init_boost_set(uint32_t value);    /* 0x08002c30 */
extern void case_init_hex_log(const uint8_t *bytes,uint32_t count); /* 0x080067c8 */
extern void case_init_secondary_read(uint32_t index,uint32_t count,uint8_t *out); /* 0x08009040 */
extern uint32_t case_init_secondary_config_read(uint32_t reg,uint32_t count,uint8_t *out); /* 0x080090ac */
extern void case_init_motion_read(uint32_t index,uint32_t count,uint8_t *out); /* 0x08008fa8 */
extern void case_init_display_reset(void);          /* 0x0800502c */
extern uint32_t case_init_usb_reset_requested(void);/* 0x08002f28 */
extern void case_init_led_show(void);               /* 0x080038a0 */
extern void case_init_usb_reset(void);              /* 0x08002b40 */
extern void case_init_sensor_finish(void);          /* 0x080035f0 */
extern void case_init_pmic_write(uint32_t address,uint32_t value); /* 0x080039c8 */
#include "case_battery_measurement_contract.h"
extern void case_init_service_start(void);          /* 0x0800d178 */
extern void case_init_service_ready(void);          /* 0x0800d218 */

static volatile uint8_t *state(void)
{return (volatile uint8_t *)(uintptr_t)0x2000087cu;}
static uint8_t logs_enabled(void)
{return *(volatile uint8_t *)(uintptr_t)0x200000bfu==0u;}
static void log0(uint32_t message)
{if(logs_enabled()){case_init_log(message,0u,0u,0u);case_init_log(CASE_STRING_ADDR(08003374),0u,0u,0u);}}
static void log1(uint32_t message,uint32_t value)
{if(logs_enabled()){case_init_log(message,value,0u,0u);case_init_log(CASE_STRING_ADDR(08003374),0u,0u,0u);}}

void case_application_initialize_2fc8(void)
{
    volatile uint8_t *s=state();
    if(logs_enabled()){
        uint32_t id0=case_init_id0(),id1=case_init_id1(),id2=case_init_id2();
        case_init_log(CASE_STRING_ADDR(08003350),id2,id1,id0);
        case_init_log(CASE_STRING_ADDR(08003374),0u,0u,0u);
    }
    for(uint32_t i=8u;i<16u;i++)s[i]=0u;
    s[1]=0u;s[2]=0u;
    s[3]=(uint8_t)(case_init_pin_read(0x50000400u,0x20u)==0u);
    s[4]=(uint8_t)(case_init_pin_read(0x50000000u,4u)==1u);
    s[0x12]=(uint8_t)(s[0]==3u);s[0x13]=(uint8_t)(s[0]==3u);
    for(uint32_t i=0x10u;i<=0x2cu;i++)
        if(i!=0x12u && i!=0x13u && i!=0x16u && i!=0x1eu && i!=0x1fu)s[i]=0u;
    s[0x15]=1u;s[0x16]=1u;
    case_init_sensor_prepare();
    uint8_t good=1u,received=0u;
    uint8_t attempts=0u;
    do{
        case_init_selfcheck_read(0u,&received,1u);
        if(received==0xa0u){log0(CASE_STRING_ADDR(080033b4));break;}
        case_init_wait(100u);
        attempts++;
    }while(attempts!=3u);
    if(received!=0xa0u){good=0u;log1(CASE_STRING_ADDR(0800337f),received);}
    case_init_pmic_prepare();
    attempts=0u;received=0u;
    for(;;){
        case_init_pmic_read(0x14u,&received,1u);
        if(received==0x14u)break;
        log0(CASE_STRING_ADDR(080033cc));
        if(received!=0u){log0(CASE_STRING_ADDR(080033e8));(void)case_init_pmic_reset(0x14u,0x14u);}
        case_init_wait(100u);attempts++;
        if(case_init_pin_read(0x50000400u,0x20u)==0u){
            attempts=0u;case_init_wait(200u);
        }else if(attempts==3u)break;
    }
    if(received==0x14u && attempts!=3u){
        uint8_t pmic[8];
        log0(CASE_STRING_ADDR(08003437));
        for(uint32_t i=0;i<8u;i++)case_init_pmic_read(0x10u+i,&pmic[i],1u);
        if(logs_enabled())case_init_log(CASE_STRING_ADDR(08003450),0u,0u,0u);
        case_init_hex_log(pmic,8u);
    }else{
        log0(CASE_STRING_ADDR(08003400));
        case_init_power_set(0u);case_init_wake_mask(0x2bu);
        case_init_wake_config(0x2020u);
        *(volatile uint32_t *)(uintptr_t)0x40007018u=0x1003fu;
        case_init_wake_clock();
    }
    uint32_t pin=case_init_pin_read(0x50000400u,0x20u);
    s[3]=(uint8_t)(pin==0u);
    case_init_boost_set(pin!=0u);
    log1(CASE_STRING_ADDR(08003464),s[3]==0u);
    case_init_wait(10u);
    received=0u;
    case_init_secondary_read(0u,1u,&received);
    if(received==0x81u){
        volatile uint8_t *adjust=(volatile uint8_t *)(uintptr_t)0x20000106u;
        (void)case_init_secondary_config_read(0xa4u,1u,(uint8_t *)(uintptr_t)adjust);
        uint8_t value=*adjust;
        *adjust=(uint8_t)(((value&7u)*2u)+((value&0x10u)!=0u?0x50u:0x60u));
        log1(CASE_STRING_ADDR(0800347f),*adjust);
    }else{good=0u;log1(CASE_STRING_ADDR(080034a0),received);}
    received=0u;
    case_init_motion_read(0u,1u,&received);
    if((received>>4)==9u){
        case_init_power_set(1u);log0(CASE_STRING_ADDR(080034d4));
        if(good!=0u)goto finish_checks;
    }else log0(CASE_STRING_ADDR(080034ec));
    for(uint32_t i=0;i<5u;i++){
        log1(CASE_STRING_ADDR(08003520),5u-i);
        case_init_wait(1000u);
    }
    case_init_display_reset();
finish_checks:
    if(case_init_usb_reset_requested()!=0u){
        log0(CASE_STRING_ADDR(0800353c));
        case_init_led_show();case_init_usb_reset();
    }
    case_init_sensor_finish();
    uint32_t scratch=0u;
    case_init_pmic_read(0x10u,(uint8_t *)&scratch,1u);
    case_init_pmic_read(0x11u,(uint8_t *)&scratch,1u);
    case_init_pmic_write(10u,0x40u);
    case_init_pmic_write(11u,0xffu);
    case_init_read_product_byte(&scratch);
    s[1]=scratch;
    case_init_service_start();
    volatile uint8_t *id=(volatile uint8_t *)(uintptr_t)0x20000090u;
    for(uint32_t i=0;i<8u;i++)case_init_secondary_read(i,1u,(uint8_t *)(uintptr_t)(id+i));
    case_init_service_ready();
}
