#include <stdint.h>
#include <stddef.h>
#include "native_gomore_runtime_configuration.h"
extern volatile uint32_t r1_gomore_native_context;
_Static_assert(sizeof(struct r1_gomore_runtime_configuration)==20,"runtime/auth record size");
volatile struct r1_gomore_runtime_configuration r1_gomore_runtime_configuration
    __attribute__((section(".r1.gomore.runtime.configuration"),aligned(4)))={.utc_offset=-1};
extern uint32_t gomore_primitives_return_zero(void);
struct __attribute__((packed,may_alias)) lower_word {uint32_t value;};
struct __attribute__((packed,may_alias)) lower_half {uint16_t value;};
static uint32_t word(uint32_t address)
{ return ((const volatile struct lower_word *)(uintptr_t)address)->value; }
static void put_word(uint32_t address,uint32_t value)
{ ((volatile struct lower_word *)(uintptr_t)address)->value=value; }
static uint16_t half(uint32_t address)
{ return ((const volatile struct lower_half *)(uintptr_t)address)->value; }
static void put_half(uint32_t address,uint16_t value)
{ ((volatile struct lower_half *)(uintptr_t)address)->value=value; }
static uint8_t byte(uint32_t address)
{ return *(const volatile uint8_t *)(uintptr_t)address; }
static void put_byte(uint32_t address,uint8_t value)
{ *(volatile uint8_t *)(uintptr_t)address=value; }
static void copy_float(uint32_t source,uint32_t destination)
{ *(volatile float *)(uintptr_t)destination=*(const volatile float *)(uintptr_t)source; }
int32_t r1_gomore_runtime_validate_native(uint32_t timestamp,uint32_t force)
{
    int32_t status=0;
    if (gomore_primitives_return_zero()) {
        if (r1_gomore_runtime_configuration.timestamp_limit<=timestamp || timestamp<=UINT32_C(0x688a4180))
            status=-1006;
    }
    if (!force && !r1_gomore_native_context) return -1;
    int32_t offset=r1_gomore_runtime_configuration.utc_offset;
    uint32_t context=r1_gomore_native_context;
    int32_t active_offset=(int16_t)half(context+0x39dau);
    if (offset!=active_offset) return -1008;
    return status;
}
void r1_gomore_copy_output_native(volatile void *packet)
{
    uint32_t destination=(uint32_t)(uintptr_t)packet+88u;
    uint32_t source=r1_gomore_native_context+384u;
    copy_float(source+164u,destination);
    put_byte(destination+4u,byte(source+172u));
    copy_float(source+212u,destination-16u);
    copy_float(source+248u,destination-12u);
    copy_float(source+252u,destination-8u);
    copy_float(source+4u,destination+72u);
    copy_float(source+8u,destination+76u);
    put_byte(destination+8u,byte(source+373u));
    put_byte(destination+9u,byte(source+374u));
    put_byte(destination+10u,byte(source+375u));
    put_word(destination+16u,word(source+324u));
    put_word(destination+20u,word(source+328u));
    put_byte(destination+24u,byte(source+350u));
    put_byte(destination+25u,byte(source+351u));
    put_byte(destination+26u,byte(source+352u));
    put_byte(destination+27u,byte(source+353u));
    put_half(destination-20u,half(source+322u));
    put_byte(destination-4u,byte(source+154u));
    put_byte(destination-37u,byte(source+153u));
    put_byte(destination+40u,byte(source+1u));
    put_byte(destination+41u,byte(source+2u));
    put_byte(destination+42u,byte(source));
    put_byte(destination+28u,byte(source+384u));
    put_byte(destination+29u,byte(source+385u));
    put_word(destination+32u,word(source+392u));
    put_half(destination+38u,half(source+400u));
    put_half(destination+36u,half(source+396u));
}
