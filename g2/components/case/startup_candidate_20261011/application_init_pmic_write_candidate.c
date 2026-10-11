/* SPDX-License-Identifier: MIT
 * Native CASE 0x29a4/0x2a00 PMIC writes and 0x39c8/0x39e4 guards.
 */
#include <stdint.h>
extern void case_pmic_bus_start(void);
extern void case_pmic_bus_write_byte(uint32_t value);
extern uint32_t case_pmic_bus_ack(void);
extern void case_pmic_bus_stop(void);
static uint32_t write_transaction(uint32_t reg,uint32_t value,uint32_t device)
{
    *(volatile uint8_t *)(uintptr_t)0x20000114u=0u;
    uint8_t retry=0u;
    do{
        case_pmic_bus_start();
        case_pmic_bus_write_byte(device);
        if(case_pmic_bus_ack()==0u)break;
        retry=(uint8_t)(retry+1u);
    }while(retry<200u);
    if(retry==200u)goto fail;
    case_pmic_bus_write_byte(reg);
    if(case_pmic_bus_ack()!=0u)goto fail;
    case_pmic_bus_write_byte(value);
    if(case_pmic_bus_ack()!=0u)goto fail;
    case_pmic_bus_stop();
    return 1u;
fail:
    case_pmic_bus_stop();
    return 0u;
}
uint32_t case_init_pmic_device_write(uint32_t reg,uint32_t value)
{return write_transaction(reg,value,0xc8u);}
uint32_t case_init_pmic_device_reset(uint32_t reg,uint32_t value)
{return write_transaction(reg,value,0x70u);}
static uint32_t guarded_write(uint32_t reg,uint32_t value,uint32_t (*writer)(uint32_t,uint32_t))
{
    volatile uint8_t *guard=(volatile uint8_t *)(uintptr_t)0x20000029u;
    if(*guard==0u){
        *guard=1u;
        (void)writer(reg,value);
        *guard=0u;
        return 0u;
    }
    return reg;
}
uint32_t case_init_pmic_write(uint32_t reg,uint32_t value)
{return guarded_write(reg,value,case_init_pmic_device_write);}
uint32_t case_init_pmic_reset(uint32_t reg,uint32_t value)
{return guarded_write(reg,value,case_init_pmic_device_reset);}
