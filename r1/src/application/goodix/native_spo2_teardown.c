#include <stdint.h>
#include "goodix_mem.h"
#include "goodix_spo2.h"
#include "native_spo2_teardown.h"
extern uint32_t r1_goodix_native_release_cell(volatile uint32_t *);
/* Shared with future native SpO2 initialization. */
void *volatile r1_goodix_native_spo2_context
    __attribute__((section(".r1.goodix.native.spo2.context"),aligned(4)));
static uint32_t load_word(uintptr_t address)
{
    return *(const volatile uint32_t *)address;
}
static void release_cell(uintptr_t address)
{
    (void)r1_goodix_native_release_cell((volatile uint32_t *)address);
}
void r1_goodix_spo2_release_pair(const void *descriptor,void *record)
{
    (void)descriptor;
    uintptr_t base=(uintptr_t)record;
    goodix_mem_free((void *)(uintptr_t)load_word(base+8));
    goodix_mem_free((void *)(uintptr_t)load_word(base+0x18));
}
void r1_goodix_spo2_release_descriptor_pair(const void *descriptor,void *record)
{
    (void)descriptor;
    uintptr_t base=(uintptr_t)record;
    release_cell(base);
    release_cell(base+0xc);
}
void r1_goodix_spo2_release_short_pair(const void *descriptor,void *record)
{
    (void)descriptor;
    uintptr_t base=(uintptr_t)record;
    release_cell(base+4);
    release_cell(base+0x10);
}
void r1_goodix_spo2_release_channel(const void *descriptor,void *record)
{
    (void)descriptor;
    uintptr_t base=(uintptr_t)record;
    static const uint8_t cells[]={0,0x10,0x20,0x30,0x40,0x54};
    for (uint32_t i=0;i<sizeof(cells);i++) release_cell(base+cells[i]);
}
void r1_goodix_spo2_release_session(const void *descriptor,void *record)
{
    uintptr_t base=(uintptr_t)record;
    r1_goodix_spo2_release_channel(descriptor,record);
    r1_goodix_spo2_release_channel(descriptor,(void *)(base+0x64));
    release_cell(base+0xc8);
    release_cell(base+0xd8);
    release_cell(base+0xe8);
    release_cell(base+0xf8);
}
void r1_goodix_spo2_release_aggregate(const void *descriptor,void *record)
{
    uintptr_t base=(uintptr_t)record;
    r1_goodix_spo2_release_descriptor_pair(descriptor,(void *)(uintptr_t)load_word(base+0x1c));
    goodix_mem_free((void *)(uintptr_t)load_word(base+0x1c));
    r1_goodix_spo2_release_short_pair(descriptor,(void *)(base+4));
    r1_goodix_spo2_release_session(descriptor,(void *)(uintptr_t)load_word(base));
    goodix_mem_free((void *)(uintptr_t)load_word(base));
}
void r1_goodix_spo2_release_owned(const void *descriptor,void *record)
{
    (void)descriptor;
    uintptr_t base=(uintptr_t)record;
    release_cell((uintptr_t)load_word(base)+4);
    goodix_mem_free((void *)(uintptr_t)load_word(base));
}
uint32_t r1_goodix_spo2_release_context_pair(void *context)
{
    if (context) {
        uint32_t allocation=load_word((uintptr_t)context+0x300);
        if (allocation) goodix_mem_free((void *)(uintptr_t)allocation);
        goodix_mem_free(context);
    }
    return 0;
}
void r1_goodix_spo2_release_context_record(const void *descriptor,void *record)
{
    (void)descriptor;
    (void)r1_goodix_spo2_release_context_pair((void *)(uintptr_t)load_word((uintptr_t)record+0x1c));
}
void r1_goodix_spo2_release_channels(const void *descriptor,void *record)
{
    uintptr_t info=(uintptr_t)descriptor;
    uintptr_t owner=(uintptr_t)record;
    if (load_word(info+0x1c)) {
        uint32_t i=0;
        for (;;) {
            uint32_t count=load_word(info);
            uintptr_t array=load_word(owner);
            if (count<=i) {
                goodix_mem_free((void *)array);
                break;
            }
            release_cell(array+i*0x28u+0x14u);
            i++;
        }
    }
}
void r1_goodix_spo2_release_buffer(void *record,const void *descriptor)
{
    (void)descriptor;
    uintptr_t owner=(uintptr_t)record;
    release_cell((uintptr_t)load_word(owner));
    uint32_t allocation=load_word(owner);
    if (allocation) {
        goodix_mem_free((void *)(uintptr_t)allocation);
        *(volatile uint32_t *)owner=0;
    }
}
goodix_spo2_ret goodix_spo2_deinit(void)
{
    if (r1_goodix_native_spo2_context) {
        uintptr_t base=(uintptr_t)r1_goodix_native_spo2_context;
        r1_goodix_spo2_release_pair((void *)(base+0xc),(void *)(base+0x6c));
        base=(uintptr_t)r1_goodix_native_spo2_context;
        r1_goodix_spo2_release_aggregate((void *)(base+0xc),(void *)(base+0x88));
        base=(uintptr_t)r1_goodix_native_spo2_context;
        r1_goodix_spo2_release_owned((void *)(base+0xc),(void *)(base+0xa8));
        base=(uintptr_t)r1_goodix_native_spo2_context;
        r1_goodix_spo2_release_context_record((void *)(base+0xc),(void *)(base+0xb0));
        base=(uintptr_t)r1_goodix_native_spo2_context;
        r1_goodix_spo2_release_channels((void *)(base+0xc),(void *)(base+0xd0));
        base=(uintptr_t)r1_goodix_native_spo2_context;
        r1_goodix_spo2_release_buffer((void *)(base+0xac),(void *)(base+0xc));
        goodix_mem_free(r1_goodix_native_spo2_context);
        r1_goodix_native_spo2_context=0;
    }
    return GX_ALGO_SPO2_SUCCESS;
}
