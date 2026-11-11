#include <stdint.h>
#include <stddef.h>
#include "native_graph_initialize.h"
#include "../../vendor/model_data/r1_model_data.h"
extern void *memmove(void *,const void *,size_t);
extern const void *r1_goodix_native_graph_family_zero_build(void *,const void *);
extern const void *r1_goodix_native_graph_family_nonzero_build(uint32_t,void *,const void *);
extern uint32_t r1_goodix_model_recurrent_descriptor(void *,uint32_t,uint32_t,uint32_t *);
extern uint32_t r1_goodix_model_dense_descriptor(void *,uint32_t,uint32_t,uint32_t,float,uint32_t,uint32_t *);
extern uint32_t r1_goodix_model_vector_get(uint32_t);
extern uint32_t r1_goodix_model_softmax_get(void);
static uint32_t word(uintptr_t p) { return *(const volatile uint32_t *)p; }
static void put(uintptr_t p,uint32_t value) { *(volatile uint32_t *)p=value; }
uint32_t r1_goodix_native_graph_initialize(void *context,const void *weights)
{
    uintptr_t p=(uintptr_t)context;
    uint32_t mode=word(p),record[6];
    /* Stock reads the header again for branch selection. */
    const void *next;
    if (word(p)) next=r1_goodix_native_graph_family_nonzero_build(mode,(void *)(p+4),weights);
    else next=r1_goodix_native_graph_family_zero_build((void *)(p+4),weights);
    uint32_t cursor=(uint32_t)(uintptr_t)next;
    (void)r1_goodix_model_recurrent_descriptor(record,8,4,&cursor);
    (void)memmove((void *)(p+0x1bc),record,24);
    put(p+0x1d4,r1_goodix_model_vector_get(1));
    const uint8_t *schema=r1_goodix_hba_tail_schema+mode*8u;
    (void)r1_goodix_model_recurrent_descriptor(record,schema[0],schema[1],&cursor);
    (void)memmove((void *)(p+0x1d8),record,24);
    (void)r1_goodix_model_recurrent_descriptor(record,schema[2],schema[3],&cursor);
    (void)memmove((void *)(p+0x1f0),record,24);
    (void)r1_goodix_model_dense_descriptor(record,schema[4],schema[5],1,0.0f,1,&cursor);
    (void)memmove((void *)(p+0x208),record,24);
    (void)r1_goodix_model_dense_descriptor(record,schema[6],schema[7],1,0.0f,0,&cursor);
    (void)memmove((void *)(p+0x220),record,24);
    uint32_t result=(uint32_t)(p+0x238);
    if (mode==2) { result=r1_goodix_model_softmax_get();put(p+0x238,result); }
    return result;
}
