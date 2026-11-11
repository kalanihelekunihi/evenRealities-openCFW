#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
#include "../../vendor/model_data/r1_model_data.h"
#include "native_spo2_initialize.h"
extern void *memset(void *,int,size_t);
/* Reuse the canonical four-stage numeric coefficient resource. */
const void *r1_goodix_hba_table_a692c_get(void) { return r1_goodix_hba_family_0_graph.words; }
const void *r1_goodix_hba_table_a04cc_get(void) { return r1_goodix_hba_mode_0_descriptors.words; }
const void *r1_goodix_hba_table_9d640_get(void) { return r1_goodix_hba_family_1_graph.words; }
const void *r1_goodix_hba_table_a50b0_get(void) { return r1_goodix_hba_second_graph.words; }
static void put32(uintptr_t p,uint32_t value) { *(volatile uint32_t *)p=value; }
uint32_t r1_goodix_native_filter_descriptor_initialize(void *record,uint32_t count,
    const void *coefficients,void *buffer)
{
    uintptr_t p=(uintptr_t)record;
    *(volatile uint8_t *)p=(uint8_t)count;
    put32(p+8,(uint32_t)(uintptr_t)coefficients);
    uint32_t bytes=count<<3;
    (void)memset(buffer,0,bytes);
    put32(p+4,(uint32_t)(uintptr_t)buffer);
    return (uint32_t)((uintptr_t)buffer+bytes);
}
uint32_t r1_goodix_native_pair_buffer_initialize(void *record,uint32_t source_count,
    const void *coefficients,float first,float second)
{
    (void)first;(void)second;
    uint32_t count=source_count>>1;
    void *buffer=goodix_mem_malloc((int32_t)(count<<3));
    /* Allocation uses the full half-count; initialization uses its low byte. */
    return r1_goodix_native_filter_descriptor_initialize(record,(uint8_t)count,coefficients,buffer);
}
uint32_t r1_goodix_hba_workspace_initialize(void *workspace)
{
    uintptr_t p=(uintptr_t)workspace;
    (void)memset(workspace,0,344);
    static const uint8_t filters[]={0x04,0x14,0x24,0x34,0x44,0x54,0x64,0x84,0x74};
    union { uint32_t bits;float value; } first={.bits=UINT32_C(0x3eaaa64c)};
    for (uint32_t i=0;i<sizeof(filters);i++)
        (void)r1_goodix_native_pair_buffer_initialize((void *)(p+filters[i]),8,
            r1_goodix_hba_filter_coefficients.words,first.value,4.0f);
    /* The stock input to ceil/conversion is the exact binary64 integer60.
     * Its unsigned result is60; no generic math replacement is admitted. */
    static const uint16_t short_records[]={0x94,0x9c,0xa4,0xac,0xb4,0xbc,0xc4,0xcc,0xd4};
    for (uint32_t i=0;i<sizeof(short_records)/sizeof(short_records[0]);i++)
        (void)r1_goodix_native_s16_queue_initialize((void *)(p+short_records[i]),NULL,i==7 ? 60 : 180);
    static const uint16_t float_records[]={0xdc,0xec,0xfc,0x10c,0x11c,0x12c,0x13c};
    for (uint32_t i=0;i<sizeof(float_records)/sizeof(float_records[0]);i++)
        (void)r1_goodix_native_float_record_initialize((void *)(p+float_records[i]),NULL,20,1);
    return 0;
}
