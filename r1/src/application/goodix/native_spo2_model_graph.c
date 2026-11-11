#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *,const void *,size_t);
/* Executor identities are unresolved data bindings, not guessed callable ABIs. */
extern const uint32_t r1_goodix_graph_convolution_executor_address;
extern const uint32_t r1_goodix_graph_aligned_executor_address;
extern const uint32_t r1_goodix_graph_pool_executor_address;
extern const uint32_t r1_goodix_graph_vector_executor_address;
extern const uint32_t r1_goodix_graph_operator_executor_address;
extern const uint32_t r1_goodix_graph_pair_executor_address;
extern const uint32_t r1_goodix_graph_quantizer_executor_address;
static uint32_t read32(uintptr_t p) { return *(const volatile uint32_t *)p; }
static void write32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }
static uint32_t float_bits(float value)
{
    union { float value;uint32_t bits; } representation={.value=value};
    return representation.bits;
}
uint32_t r1_goodix_graph_convolution_descriptor(void *out,uint32_t a,uint32_t b,
    uint32_t c,float scale,uint32_t d,uint32_t inputs,uint32_t outputs,
    uint32_t groups,uint32_t ignored,uint32_t flag,uint32_t *cursor)
{
    (void)ignored;
    uint32_t record[6]={0};
    record[0]=(uint8_t)a|((uint32_t)(uint8_t)b<<8)|((uint32_t)(uint8_t)c<<16)|((uint32_t)(uint8_t)d<<24);
    record[1]=(uint8_t)inputs|((uint32_t)(uint8_t)outputs<<8)|((uint32_t)(uint8_t)groups<<16)|((uint32_t)(uint8_t)flag<<24);
    record[2]=float_bits(scale);
    /* Stock callers supply nonzero groups. */
    uint32_t count=a*(inputs/groups)*outputs,start=read32((uintptr_t)cursor);
    record[3]=start;record[4]=start+(count<<2);
    write32((uintptr_t)cursor,start+(outputs<<2)+(count<<2));
    record[5]=r1_goodix_graph_convolution_executor_address;
    (void)memmove(out,record,24);
    return (uint32_t)((uintptr_t)out+24);
}
uint32_t r1_goodix_graph_aligned_descriptor(void *out,uint32_t a,uint32_t b,
    uint32_t c,float scale,uint32_t d,uint32_t inputs,uint32_t outputs,
    uint32_t groups,uint32_t ignored,uint32_t flag,uint32_t *cursor)
{
    (void)ignored;
    uint32_t record[6]={0};
    record[0]=(uint8_t)a|((uint32_t)(uint8_t)b<<8)|((uint32_t)(uint8_t)c<<16)|((uint32_t)(uint8_t)d<<24);
    record[1]=(uint8_t)inputs|((uint32_t)(uint8_t)outputs<<8)|((uint32_t)(uint8_t)groups<<16)|((uint32_t)(uint8_t)flag<<24);
    record[2]=float_bits(scale);
    uint32_t span=(a*(inputs/groups)*outputs+3u)&~UINT32_C(3);
    uint32_t start=read32((uintptr_t)cursor),next=start+span;
    record[3]=start;record[4]=next+(outputs<<2)+8u;
    write32((uintptr_t)cursor,next+(outputs<<3)+24u);
    record[5]=r1_goodix_graph_aligned_executor_address;
    (void)memmove(out,record,24);
    return (uint32_t)((uintptr_t)out+24);
}
void *r1_goodix_graph_pool_descriptor(void *out,uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{
    write32((uintptr_t)out,(uint8_t)a|((uint32_t)(uint8_t)b<<8)|((uint32_t)(uint8_t)c<<16)|((uint32_t)(uint8_t)d<<24));
    write32((uintptr_t)out+4,r1_goodix_graph_pool_executor_address);
    return out;
}
uint32_t r1_goodix_graph_vector_get(void) { return r1_goodix_graph_vector_executor_address; }
void *r1_goodix_graph_operator_descriptor(void *out,uint32_t flag,float scale)
{
    write32((uintptr_t)out,(uint8_t)flag);
    write32((uintptr_t)out+4,float_bits(scale));
    write32((uintptr_t)out+8,0);
    write32((uintptr_t)out+12,r1_goodix_graph_operator_executor_address);
    return out;
}
void *r1_goodix_graph_pair_descriptor(void *out,uint32_t *cursor)
{
    uint32_t start=read32((uintptr_t)cursor);
    uint32_t first=read32(start),second=read32(start+4u);
    write32((uintptr_t)cursor,start+8u);
    write32((uintptr_t)out,0);write32((uintptr_t)out+4,first);
    write32((uintptr_t)out+8,second);write32((uintptr_t)out+12,r1_goodix_graph_pair_executor_address);
    return out;
}
void *r1_goodix_graph_quantizer_descriptor(void *out,uint32_t *cursor)
{
    uint32_t first=0,second=UINT32_C(0x3f800000);
    if (cursor) {
        uint32_t start=read32((uintptr_t)cursor);
        first=read32(start);second=read32(start+4u);
        write32((uintptr_t)cursor,start+8u);
    }
    write32((uintptr_t)out,first);write32((uintptr_t)out+4,second);
    write32((uintptr_t)out+8,r1_goodix_graph_quantizer_executor_address);
    return out;
}
const void *r1_goodix_model_graph_build(void *destination,const void *weights)
{
    uint8_t *out=destination;
    uint32_t cursor=(uint32_t)(uintptr_t)weights,record[6];
    r1_goodix_graph_quantizer_descriptor(record,&cursor);
    (void)memmove(out,record,12);
#define ALIGNED(offset,a,b,c,d,e,f,g,h) \
    r1_goodix_graph_aligned_descriptor(record,a,b,c,0.0f,d,e,f,g,1,h,&cursor); \
    (void)memmove(out+offset,record,24)
#define CONV(offset,a,b,c,d,e,f,g,h) \
    r1_goodix_graph_convolution_descriptor(record,a,b,c,0.0f,d,e,f,g,1,h,&cursor); \
    (void)memmove(out+offset,record,24)
#define POOL(offset) \
    r1_goodix_graph_pool_descriptor(record,0,2,2,0); \
    (void)memmove(out+offset,record,8)
    ALIGNED(0x00c,5,1,2,2,1,16,1,0);
    POOL(0x024);
    ALIGNED(0x02c,1,1,0,0,16,4,1,1);
    ALIGNED(0x044,3,1,1,1,4,4,4,1);
    ALIGNED(0x05c,1,1,0,0,4,16,1,0);
    r1_goodix_graph_pair_descriptor(record,&cursor);
    (void)memmove(out+0x074,record,16);
    POOL(0x084);
    ALIGNED(0x08c,1,1,0,0,16,4,1,1);
    ALIGNED(0x0a4,3,1,1,1,4,4,4,1);
    ALIGNED(0x0bc,1,1,0,0,4,16,1,0);
    r1_goodix_graph_pair_descriptor(record,&cursor);
    (void)memmove(out+0x0d4,record,16);
    POOL(0x0e4);
    write32((uintptr_t)out+0x0ec,r1_goodix_graph_vector_get());
    CONV(0x108,1,1,0,0,16,1,1,1);
    CONV(0x120,3,1,1,1,1,1,1,1);
    CONV(0x138,1,1,0,0,1,8,1,0);
    CONV(0x0f0,1,1,0,0,16,8,1,0);
    r1_goodix_graph_operator_descriptor(record,1,0.0f);
    (void)memmove(out+0x150,record,16);
#undef ALIGNED
#undef CONV
#undef POOL
    return (const void *)(uintptr_t)cursor;
}
