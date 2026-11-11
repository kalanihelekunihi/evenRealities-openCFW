#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
extern void *memmove(void *,const void *,size_t);
extern void *memset(void *,int,size_t);
extern uint32_t r1_goodix_graph_aligned_descriptor(void *,uint32_t,uint32_t,uint32_t,float,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *);
extern void *r1_goodix_graph_quantizer_descriptor(void *,uint32_t *);
extern void *r1_goodix_graph_pair_descriptor(void *,uint32_t *);
extern void *r1_goodix_graph_pool_descriptor(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_goodix_graph_vector_get(void);
extern const uint32_t r1_goodix_graph_merge_executor_address;
static uint32_t byte(uintptr_t p) { return *(const volatile uint8_t *)p; }
static void put(uintptr_t p,uint32_t value) { *(volatile uint32_t *)p=value; }
uint32_t r1_goodix_graph_merge_vector_get(uint32_t selector)
{ (void)selector;return r1_goodix_graph_merge_executor_address; }
static void aligned(void *destination,uint32_t kernel,uint32_t padding,uint32_t inputs,
    uint32_t outputs,uint32_t groups,uint32_t flag,uint32_t *cursor)
{
    uint32_t record[6];
    (void)r1_goodix_graph_aligned_descriptor(record,kernel,1,padding,0.0f,padding,inputs,outputs,groups,1,flag,cursor);
    (void)memmove(destination,record,24);
}
const void *r1_goodix_native_layer_block_build(void *destination,const void *weights,const void *configuration)
{
    uintptr_t out=(uintptr_t)destination,cfg=(uintptr_t)configuration;
    uint32_t cursor=(uint32_t)(uintptr_t)weights,record[6];
    uint32_t outputs=byte(cfg+1),inputs=byte(cfg);
    aligned((void *)out,1,0,inputs,outputs,1,1,&cursor);
    outputs=byte(cfg+2);inputs=byte(cfg+1);
    aligned((void *)(out+0x18),1,0,inputs,outputs,1,1,&cursor);
    r1_goodix_graph_quantizer_descriptor(record,&cursor);(void)memmove((void *)(out+0x30),record,12);
    outputs=byte(cfg+3);inputs=byte(cfg+2);
    aligned((void *)(out+0x3c),1,0,inputs,outputs,1,1,&cursor);
    outputs=byte(cfg+4);inputs=byte(cfg+3);
    /* The native depthwise descriptor requires a nonzero live group byte. */
    aligned((void *)(out+0x54),3,1,inputs,outputs,outputs,1,&cursor);
    outputs=byte(cfg+5);inputs=byte(cfg+4);
    aligned((void *)(out+0x6c),1,0,inputs,outputs,1,0,&cursor);
    put(out+0x84,0);
    if (byte(cfg+6)) {
        put(out+0x84,1);
        outputs=byte(cfg+6);inputs=byte(cfg);
        aligned((void *)(out+0x88),1,0,inputs,outputs,1,0,&cursor);
    }
    r1_goodix_graph_pair_descriptor(record,&cursor);(void)memmove((void *)(out+0xa0),record,16);
    return (const void *)(uintptr_t)cursor;
}
void *r1_goodix_native_graph_mode6_create(const void *weights,const uint32_t *parameters)
{
    (void)parameters;
    uint8_t *instance=goodix_mem_malloc(984);
    if (!instance) return NULL;
    (void)memset(instance,0,984);put((uintptr_t)instance,6);
    uint32_t cursor=(uint32_t)(uintptr_t)weights,record[6];
    r1_goodix_graph_quantizer_descriptor(record,&cursor);(void)memmove(instance+4,record,12);
    aligned(instance+0x10,5,2,4,10,1,0,&cursor);
    static const uint8_t layers[5][8]={
        {10,2,10,1,1,1,1,0},{4,1,4,1,1,1,1,0},{24,2,24,15,15,24,0,0},
        {24,8,24,16,16,16,16,0},{16,1,16,5,5,1,1,0}
    };
    cursor=(uint32_t)(uintptr_t)r1_goodix_native_layer_block_build(instance+0x28,(const void *)(uintptr_t)cursor,layers[0]);
    aligned(instance+0xd8,5,2,1,4,1,0,&cursor);
    cursor=(uint32_t)(uintptr_t)r1_goodix_native_layer_block_build(instance+0xf0,(const void *)(uintptr_t)cursor,layers[1]);
    put((uintptr_t)instance+0x1a0,r1_goodix_graph_merge_vector_get(0));
    aligned(instance+0x1a4,5,2,4,24,1,0,&cursor);
    cursor=(uint32_t)(uintptr_t)r1_goodix_native_layer_block_build(instance+0x1bc,(const void *)(uintptr_t)cursor,layers[2]);
    cursor=(uint32_t)(uintptr_t)r1_goodix_native_layer_block_build(instance+0x26c,(const void *)(uintptr_t)cursor,layers[3]);
    (void)r1_goodix_native_layer_block_build(instance+0x31c,(const void *)(uintptr_t)cursor,layers[4]);
    r1_goodix_graph_pool_descriptor(record,1,3,3,0);(void)memmove(instance+0x3cc,record,8);
    put((uintptr_t)instance+0x3d4,r1_goodix_graph_vector_get());
    return instance;
}
