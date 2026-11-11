#include <stdint.h>
#include <stddef.h>
extern volatile uint32_t r1_gomore_native_context;
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_gomore_sleep_interval_run_native(uint32_t,uint32_t,uint32_t,uint32_t,volatile void *);
extern uint32_t r1_gomore_propagate_packed_status_native(uint32_t,volatile void *,volatile void *);
struct __attribute__((packed,may_alias)) interval_word { uint32_t value; };

uint32_t r1_gomore_sleep_interval_update_native(uint32_t mode,volatile void *output)
{
    uint32_t context=r1_gomore_native_context;
    *(volatile uint8_t *)(uintptr_t)(context+734u)=0;
    if (output) __aeabi_memclr((void *)output,56);
    _Alignas(8) volatile uint8_t record[32];
    volatile uint32_t propagated;
    __aeabi_memclr((void *)record,32);
    context=r1_gomore_native_context;
    (void)r1_gomore_sleep_interval_run_native(context+4400u,context+400u,context+396u,mode,record);
    if (output) {
        volatile uint8_t *bytes=output;
        ((volatile struct interval_word *)bytes)->value=((volatile struct interval_word *)record)->value;
        ((volatile struct interval_word *)(bytes+4))->value=((volatile struct interval_word *)(record+4))->value;
        bytes[8]=record[26];
        bytes[9]=record[27];
        bytes[10]=record[28];
        bytes[11]=record[29];
    }
    context=r1_gomore_native_context;
    if (*(volatile uint8_t *)(uintptr_t)(context+14757u)!=3)
        (void)r1_gomore_propagate_packed_status_native(context+5112u,record,&propagated);
    return 0;
}
