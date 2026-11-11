#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"

volatile uint8_t r1_wear_adt_history[20]
    __attribute__((section(".bss.r1.wear.adt.history"),aligned(4)));
extern volatile uint8_t r1_wear_adt_active;
extern volatile uint32_t r1_wear_adt_count;
extern void *r1_native_memory_move(void *,const void *,size_t);
extern void r1_wear_probe_teardown(void);

__attribute__((section(".text.r1_wear_adt_sample_native")))
void r1_wear_adt_sample_native(uint32_t context,uint32_t payload,uint32_t length)
{
    (void)context;(void)length;
    uint32_t previous=r1_wear_adt_active;
    if (previous) {
        uintptr_t address=(uintptr_t)r1_wear_adt_history+previous*4u-4u;
        r1_wear_adt_count=read32((const volatile uint8_t *)address);
    }
    uint32_t count=*(const volatile uint8_t *)(uintptr_t)payload;
    r1_wear_adt_active=(uint8_t)count;
    if (count) {
        (void)r1_native_memory_move((void *)r1_wear_adt_history,
            (const void *)(uintptr_t)(payload+4u),count*4u);
    }
}

__attribute__((section(".text.r1_wear_adt_timeout_native")))
void r1_wear_adt_timeout_native(void)
{
    r1_wear_probe_teardown();
}
