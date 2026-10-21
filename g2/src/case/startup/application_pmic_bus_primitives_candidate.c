/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800a3d2..0xa574 software PMIC two-wire bus.
 */
#include <stdint.h>
static uint32_t mode(void){return *(volatile uint8_t *)(uintptr_t)0x20000114u;}
static void pin(uint32_t mask,uint32_t value)
{*(volatile uint32_t *)(uintptr_t)(0x50000400u+(value?24u:40u))=mask;}
static void data(uint32_t value){pin(mode()?16u:8u,value);}
static void clock(uint32_t value){pin(mode()?8u:16u,value);}
static uint32_t sample(void)
{return (*(volatile uint32_t *)(uintptr_t)0x50000410u&(mode()?8u:16u))!=0u;}
static void short_delay(void)
{for(volatile uint8_t n=0u;n<10u;n=(uint8_t)(n+1u))__asm__ volatile("nop");}
void case_pmic_bus_ack_continue(void)
{data(0u);short_delay();clock(0u);short_delay();data(1u);short_delay();data(0u);short_delay();clock(1u);short_delay();}
void case_pmic_bus_ack_last(void)
{clock(1u);short_delay();data(1u);short_delay();data(0u);short_delay();}
uint32_t case_pmic_bus_read_byte(void)
{
    uint8_t value=0u;
    for(uint8_t i=0u;i<8u;i=(uint8_t)(i+1u)){
        value=(uint8_t)(value<<1);
        data(1u);short_delay();
        if(sample())value=(uint8_t)(value+1u);
        data(0u);short_delay();
    }
    return value;
}
void case_pmic_bus_write_byte(uint32_t value)
{
    uint8_t byte=(uint8_t)value;
    for(uint8_t i=0u;i<8u;i=(uint8_t)(i+1u)){
        clock((byte&0x80u)!=0u);short_delay();
        data(1u);short_delay();
        data(0u);short_delay();
        if(i==7u){clock(1u);short_delay();}
        byte=(uint8_t)(byte<<1);
    }
}
void case_pmic_bus_start(void)
{data(1u);clock(1u);short_delay();clock(0u);short_delay();data(0u);short_delay();}
void case_pmic_bus_stop(void)
{clock(0u);data(1u);short_delay();clock(1u);short_delay();}
uint32_t case_pmic_bus_ack(void)
{
    clock(1u);data(1u);short_delay();
    uint32_t value=sample();
    data(0u);short_delay();
    return value!=0u;
}
