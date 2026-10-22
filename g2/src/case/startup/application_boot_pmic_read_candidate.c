/* SPDX-License-Identifier: MIT
 * Native CASE 0x080028b4/0x292c PMIC transaction readers and 0x35b8/0x35d4 guards.
 */
#include <stdint.h>
extern void case_pmic_bus_start(void); /* 0xa4b4 */
extern void case_pmic_bus_write_byte(uint32_t value); /* 0xa46c */
extern uint32_t case_pmic_bus_ack(void); /* 0xa4fa */
extern void case_pmic_bus_stop(void); /* 0xa4dc */
extern uint32_t case_pmic_bus_read_byte(void); /* 0xa436 */
extern void case_pmic_bus_ack_continue(void); /* 0xa3d2 */
extern void case_pmic_bus_ack_last(void); /* 0xa414 */
static uint32_t read_transaction(uint32_t selector,uint8_t *out,uint32_t count,uint32_t address_write,uint32_t address_read)
{
    *(volatile uint8_t *)(uintptr_t)0x20000114u=0u;
    case_pmic_bus_start();
    case_pmic_bus_write_byte(address_write);
    if(case_pmic_bus_ack()!=0u)goto fail;
    case_pmic_bus_write_byte(selector);
    if(case_pmic_bus_ack()!=0u)goto fail;
    case_pmic_bus_start();
    case_pmic_bus_write_byte(address_read);
    if(case_pmic_bus_ack()!=0u)goto fail;
    for(uint32_t i=0u;i<count;i=(uint16_t)(i+1u)){
        out[i]=(uint8_t)case_pmic_bus_read_byte();
        if(i==count-1u)case_pmic_bus_ack_last();
        else case_pmic_bus_ack_continue();
    }
    case_pmic_bus_stop();
    return 1u;
fail:
    case_pmic_bus_stop();
    return 0u;
}
uint32_t case_policy_timer_device_read(uint32_t selector,uint8_t *out,uint32_t count)
{return read_transaction(selector,out,count,0xc8u,0xc9u);}
uint32_t case_init_pmic_device_read(uint32_t selector,uint8_t *out,uint32_t count)
{return read_transaction(selector,out,count,0x70u,0x71u);}
static uint32_t guarded_read(uint32_t selector,uint8_t *out,uint32_t count,uint32_t (*reader)(uint32_t,uint8_t *,uint32_t))
{
    volatile uint8_t *guard=(volatile uint8_t *)(uintptr_t)0x20000029u;
    if(*guard==0u){
        *guard=1u;
        (void)reader(selector,out,count);
        *guard=0u;
        return 0u;
    }
    return selector;
}
/* Stock 0x080035B8 (case_run_guarded) */
uint32_t case_init_selfcheck_read(uint32_t selector,uint8_t *out,uint32_t count)
{return guarded_read(selector,out,count,case_policy_timer_device_read);}
/* Stock 0x080035D4 (peripheral_transaction_guard) */
uint32_t case_init_pmic_read(uint32_t selector,uint8_t *out,uint32_t count)
{return guarded_read(selector,out,count,case_init_pmic_device_read);}
