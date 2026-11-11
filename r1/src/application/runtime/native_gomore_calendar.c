#include <stdint.h>
struct __attribute__((packed,may_alias)) calendar_word { uint32_t value; };
struct __attribute__((packed,may_alias)) calendar_half { uint16_t value; };
uint32_t r1_gomore_epoch_to_civil_native(uint32_t timestamp,volatile void *output)
{
    uint32_t address=(uint32_t)(uintptr_t)output;
    ((volatile struct calendar_half *)(uintptr_t)(address+6u))->value=0;
    ((volatile struct calendar_word *)(uintptr_t)address)->value=timestamp;
    *(volatile uint8_t *)(uintptr_t)(address+12u)=timestamp%60u;
    uint32_t minutes=timestamp/60u;
    *(volatile uint8_t *)(uintptr_t)(address+11u)=minutes%60u;
    uint32_t hours=minutes/60u;
    *(volatile uint8_t *)(uintptr_t)(address+10u)=hours%24u;
    uint32_t days=hours/24u;
    uint32_t adjustment=(102032u+days*4u)/146097u+15u;
    uint32_t julian=days+adjustment-adjustment/4u+2442113u;
    uint32_t year=(julian*20u-2442u)/7305u;
    uint32_t ordinal=julian-year*365u-year/4u;
    uint32_t month=ordinal*1000u/30601u;
    uint32_t day=ordinal-month*30u-month*601u/1000u;
    if (month<=13u) { year-=4716u;month-=1u; }
    else { year-=4715u;month-=13u; }
    ((volatile struct calendar_half *)(uintptr_t)(address+4u))->value=year;
    *(volatile uint8_t *)(uintptr_t)(address+8u)=month;
    *(volatile uint8_t *)(uintptr_t)(address+9u)=day;
    return month;
}
