#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *,const void *,size_t);
extern uint32_t r1_goodix_graph_aligned_descriptor(void *,uint32_t,uint32_t,uint32_t,float,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *);
extern uint32_t r1_goodix_graph_convolution_descriptor(void *,uint32_t,uint32_t,uint32_t,float,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *);
extern void *r1_goodix_graph_quantizer_descriptor(void *,uint32_t *);
extern void *r1_goodix_graph_pair_descriptor(void *,uint32_t *);
extern void *r1_goodix_graph_pool_descriptor(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void *r1_goodix_graph_operator_descriptor(void *,uint32_t,float);
extern uint32_t r1_goodix_graph_vector_get(void);
/* Opaque executor identity data bindings; no callable ABI is assumed. */
extern const uint32_t r1_goodix_graph_transform_executor_address;
extern const uint32_t r1_goodix_graph_alternate_pool_executor_address;
extern const uint32_t r1_goodix_graph_tail_vector_executor_address;
static void put(uintptr_t p,uint32_t value) { *(volatile uint32_t *)p=value; }
void *r1_goodix_graph_packed_transform_descriptor(void *out,const void *configuration)
{
    uintptr_t p=(uintptr_t)configuration;
    uint32_t a=*(const volatile uint8_t *)p;
    uint32_t b=*(const volatile uint8_t *)(p+1);
    uint32_t c=*(const volatile uint8_t *)(p+2);
    put((uintptr_t)out,a|(b<<8)|(c<<16));
    put((uintptr_t)out+4,r1_goodix_graph_transform_executor_address);
    return out;
}
void *r1_goodix_graph_alternate_pool_descriptor(void *out,uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{
    put((uintptr_t)out,(uint8_t)a|((uint32_t)(uint8_t)b<<8)|((uint32_t)(uint8_t)c<<16)|((uint32_t)(uint8_t)d<<24));
    put((uintptr_t)out+4,r1_goodix_graph_alternate_pool_executor_address);
    return out;
}
uint32_t r1_goodix_graph_tail_vector_get(void) { return r1_goodix_graph_tail_vector_executor_address; }
struct shape { uint16_t offset;uint8_t a,b,c,d,inputs,outputs,groups,flag; };
static void descriptor(uint8_t *out,uint32_t *cursor,const struct shape *shape,uint32_t aligned)
{
    uint32_t record[6];
    if (aligned) (void)r1_goodix_graph_aligned_descriptor(record,shape->a,shape->b,shape->c,0.0f,shape->d,shape->inputs,shape->outputs,shape->groups,1,shape->flag,cursor);
    else (void)r1_goodix_graph_convolution_descriptor(record,shape->a,shape->b,shape->c,0.0f,shape->d,shape->inputs,shape->outputs,shape->groups,1,shape->flag,cursor);
    (void)memmove(out+shape->offset,record,24);
}
static const void *build(void *destination,const void *weights,uint32_t nonzero,uint32_t family)
{
    static const struct shape aligned[2][7]={
        {{0xc,5,1,2,2,4,27,1,0},{0x2c,1,1,0,0,27,14,1,1},{0x44,3,1,1,1,14,14,14,1},{0x5c,1,1,0,0,14,27,1,0},
         {0x94,1,1,0,0,27,7,1,1},{0xac,3,1,1,1,7,7,7,1},{0xc4,1,1,0,0,7,27,1,0}},
        {{0xc,5,1,2,2,4,32,1,0},{0x2c,1,1,0,0,32,1,1,1},{0x44,3,1,1,1,1,1,1,1},{0x5c,1,1,0,0,1,32,1,0},
         {0x94,1,1,0,0,32,2,1,1},{0xac,3,1,1,1,2,2,2,1},{0xc4,1,1,0,0,2,32,1,0}}
    };
    static const uint8_t output_channels[8]={8,4,8,0,0,0,0,0};
    uint8_t *out=destination;uint32_t record[6],cursor=(uint32_t)(uintptr_t)weights;
    /* Family0's private quantizer constants are exactly the default0.0/1.0;
     * unlike nonzero families, they do not consume the model cursor. */
    r1_goodix_graph_quantizer_descriptor(record,nonzero ? &cursor : NULL);
    (void)memmove(out,record,12);
    descriptor(out,&cursor,&aligned[nonzero][0],1);
    r1_goodix_graph_pool_descriptor(record,0,2,2,0);(void)memmove(out+0x24,record,8);
    for (uint32_t i=1;i<4;i++) descriptor(out,&cursor,&aligned[nonzero][i],1);
    r1_goodix_graph_pair_descriptor(record,&cursor);(void)memmove(out+0x78,record,16);
    r1_goodix_graph_pool_descriptor(record,0,2,2,0);(void)memmove(out+0x88,record,8);
    for (uint32_t i=4;i<7;i++) descriptor(out,&cursor,&aligned[nonzero][i],1);
    r1_goodix_graph_pair_descriptor(record,&cursor);(void)memmove(out+0xe0,record,16);
    r1_goodix_graph_pool_descriptor(record,0,2,2,0);(void)memmove(out+0xf0,record,8);
    put((uintptr_t)out+0x90,r1_goodix_graph_vector_get());
    uint8_t configuration[3]={0,2,1};
    r1_goodix_graph_packed_transform_descriptor(record,configuration);(void)memmove(out+0xf8,record,8);
    uint32_t width=nonzero ? 32 : 27;
    r1_goodix_graph_alternate_pool_descriptor(record,1,width,width,0);(void)memmove(out+0x100,record,8);
    struct shape tail={0x108,1,1,0,0,12,12,1,1};descriptor(out,&cursor,&tail,0);
    tail.offset=0x120;tail.flag=2;descriptor(out,&cursor,&tail,0);
    configuration[0]=0;configuration[1]=1;configuration[2]=2;
    r1_goodix_graph_packed_transform_descriptor(record,configuration);(void)memmove(out+0x138,record,8);
    put((uintptr_t)out+0x140,r1_goodix_graph_tail_vector_get());
    uint32_t middle=nonzero ? 1 : 11;
    tail=(struct shape){0x15c,1,1,0,0,(uint8_t)width,(uint8_t)middle,1,1};descriptor(out,&cursor,&tail,0);
    tail=(struct shape){0x174,3,1,1,1,(uint8_t)middle,(uint8_t)middle,(uint8_t)middle,1};descriptor(out,&cursor,&tail,0);
    uint8_t outputs=nonzero ? output_channels[family] : 8;
    tail=(struct shape){0x18c,1,1,0,0,(uint8_t)middle,outputs,1,0};descriptor(out,&cursor,&tail,0);
    tail=(struct shape){0x144,1,1,0,0,(uint8_t)width,outputs,1,0};descriptor(out,&cursor,&tail,0);
    r1_goodix_graph_operator_descriptor(record,1,0.0f);(void)memmove(out+0x1a8,record,16);
    return (const void *)(uintptr_t)cursor;
}
const void *r1_goodix_native_graph_family_zero_build(void *out,const void *weights)
{ return build(out,weights,0,0); }
/* The native local width table contains eight bytes. */
const void *r1_goodix_native_graph_family_nonzero_build(uint32_t family,void *out,const void *weights)
{ return build(out,weights,1,family); }
