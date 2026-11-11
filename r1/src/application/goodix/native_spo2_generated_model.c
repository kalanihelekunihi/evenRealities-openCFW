#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
extern void *memmove(void *,const void *,size_t);
extern void *memset(void *,int,size_t);
/* The generated graph and executor-address bindings remain unresolved.
 * Address words are opaque here: no guessed executor calling ABI is used. */
extern const void *r1_goodix_model_graph_build(void *,const void *);
extern const uint32_t r1_goodix_model_dense_executor_address;
extern const uint32_t r1_goodix_model_recurrent_executor_address;
extern const uint32_t r1_goodix_model_softmax_executor_address;
extern const uint32_t r1_goodix_model_vector_executor_address;
static uint32_t word(uintptr_t p) { return *(const volatile uint32_t *)p; }
static void put32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }
uint32_t r1_goodix_model_softmax_get(void)
{
    return r1_goodix_model_softmax_executor_address;
}
uint32_t r1_goodix_model_vector_get(uint32_t selector)
{
    (void)selector;
    return r1_goodix_model_vector_executor_address;
}
uint32_t r1_goodix_model_dense_descriptor(void *out,uint32_t rows,uint32_t columns,
    uint32_t first_flag,float scale,uint32_t second_flag,uint32_t *cursor)
{
    union { float value;uint32_t bits; } representation={.value=scale};
    uint32_t record[6]={0};
    record[0]=columns;
    record[1]=(uint8_t)first_flag|((uint32_t)(uint8_t)second_flag<<8);
    record[2]=representation.bits;
    uint32_t start=word((uintptr_t)cursor),count=rows*columns;
    record[3]=start;record[4]=start+(count<<2);
    put32((uintptr_t)cursor,start+(columns<<2)+(count<<2));
    record[5]=r1_goodix_model_dense_executor_address;
    (void)memmove(out,record,24);
    return (uint32_t)((uintptr_t)out+24);
}
uint32_t r1_goodix_model_recurrent_descriptor(void *out,uint32_t units,uint32_t inputs,uint32_t *cursor)
{
    uint32_t record[6]={0};
    uint32_t bytes=units<<2;
    record[0]=units;
    void *allocation=goodix_mem_malloc((int32_t)bytes);
    record[1]=(uint32_t)(uintptr_t)allocation;
    /* Stock clears before checking the allocation, including zero-size calls. */
    (void)memset(allocation,0,bytes);
    if (allocation) {
        uint32_t input_span=(units*inputs*3u+3u)&~UINT32_C(3);
        uint32_t recurrent_span=(units*units*3u+3u)&~UINT32_C(3);
        uint32_t start=word((uintptr_t)cursor);
        record[2]=start;record[3]=start+input_span;record[4]=start+input_span+recurrent_span;
        put32((uintptr_t)cursor,record[4]+((units*10u+6u)<<2));
        record[5]=r1_goodix_model_recurrent_executor_address;
    }
    (void)memmove(out,record,24);
    return (uint32_t)((uintptr_t)out+24);
}
void *r1_goodix_spo2_generated_model_create(const void *weights)
{
    uint8_t *instance=goodix_mem_malloc(836);
    if (!instance) return NULL;
    const void *next=r1_goodix_model_graph_build(instance+4,weights);
    next=r1_goodix_model_graph_build(instance+356,next);
    uint32_t cursor=(uint32_t)(uintptr_t)next;
    (void)r1_goodix_model_dense_descriptor(instance+708,120,8,1,0.0f,1,&cursor);
    (void)r1_goodix_model_dense_descriptor(instance+732,8,3,1,0.0f,0,&cursor);
    put32((uintptr_t)instance+756,r1_goodix_model_softmax_get());
    put32((uintptr_t)instance+760,r1_goodix_model_vector_get(1));
    (void)r1_goodix_model_recurrent_descriptor(instance+764,16,123,&cursor);
    (void)r1_goodix_model_dense_descriptor(instance+788,16,12,1,0.0f,1,&cursor);
    (void)r1_goodix_model_dense_descriptor(instance+812,12,1,1,0.0f,0,&cursor);
    return instance;
}
