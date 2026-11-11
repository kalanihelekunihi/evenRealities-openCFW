#include "native_gomore_record8.h"
#include "../board/native_battery_memory.h"
extern volatile uint32_t r1_gomore_native_context;
uint32_t r1_gomore_record8_valid_native(const volatile void *context,const volatile void *input)
{
    (void)context;
    const volatile uint8_t *record=input;
    if((uint32_t)((int32_t)(int16_t)read16(record)-15)>=46u)return 0;
    if((uint32_t)(int32_t)(int16_t)read16(record+2)>=241u)return 0;
    return record[6]<24u && record[7]<24u;
}
uintptr_t r1_gomore_record8_select_native(volatile void *output,const volatile void *input,uint32_t mode)
{
    volatile uint8_t *out=output;
    const volatile uint8_t *context=input;
    const volatile uint8_t *source=mode?(const volatile uint8_t *)(uintptr_t)(read32(context+312)+2u):context+304;
    write32(out,read32(source));write32(out+4,read32(source+4));
    return (uintptr_t)output;
}
uint32_t r1_gomore_record8_commit_native(volatile void *input,const volatile void *record_input)
{
    volatile uint8_t *context=input;
    const volatile uint8_t *record=record_input;
    if(!r1_gomore_record8_valid_native(context,record))return 1;
    volatile uint8_t *destination=(volatile uint8_t *)(uintptr_t)(read32(context+312)+2u);
    write32(destination,read32(record));write32(destination+4,read32(record+4));
    if(!context[184] && !context[180]){
        write32(context+304,read32(record));write32(context+308,read32(record+4));
    }
    return 0;
}
uint32_t r1_gomore_record8_get_native(uint32_t mode,volatile void *output)
{
    _Alignas(4) volatile uint8_t record[8];
    const volatile void *context=(const volatile void *)(uintptr_t)(r1_gomore_native_context+4400u);
    (void)r1_gomore_record8_select_native(record,context,mode);
    volatile uint8_t *out=output;
    write32(out,read32(record));write32(out+4,read32(record+4));
    return 0;
}
uint32_t r1_gomore_record8_apply_native(const volatile void *record)
{
    volatile void *context=(volatile void *)(uintptr_t)(r1_gomore_native_context+4400u);
    (void)r1_gomore_record8_commit_native(context,record);
    return 0;
}
