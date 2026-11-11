#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "goodix_mem.h"
#include "goodix_nadt.h"
#include "native_nadt_state.h"
extern bool goodix_primitives_byte_fill(uint8_t,uint8_t *,size_t);
/* Canonical state and workspace for future native initialization/calculation. */
volatile struct r1_goodix_native_nadt_state r1_goodix_native_nadt_state
    __attribute__((section(".r1.goodix.native.nadt.state"),aligned(4)));
struct r1_goodix_native_nadt_workspace r1_goodix_native_nadt_workspace
    __attribute__((section(".bss.r1.goodix.native.nadt.workspace"),aligned(4)));
goodix_primitives_nadt_stream_workspace_view
r1_goodix_native_nadt_workspace_view(void)
{
    struct r1_goodix_native_nadt_workspace *const workspace =
        &r1_goodix_native_nadt_workspace;
    return (goodix_primitives_nadt_stream_workspace_view){
        .primary_raw = workspace->first,
        .primary_filtered = workspace->second,
        .configuration_markers = workspace->small,
        .secondary_history = workspace->third,
        .primary_capacity = 100u,
        .secondary_capacity = 200u,
    };
}
const float r1_goodix_native_nadt_denominator[6]
    __attribute__((section(".r1.goodix.native.nadt.denominator"),aligned(4)))=
    {8192.0f,-9464.0f,4791.0f,8192.0f,-7316.0f,1845.0f};
const float r1_goodix_native_nadt_numerator[6]
    __attribute__((section(".r1.goodix.native.nadt.numerator"),aligned(4)))=
    {880.0f,1759.0f,880.0f,680.0f,1360.0f,680.0f};
static void zero_bytes(void *buffer,uint32_t length)
{
    (void)goodix_primitives_byte_fill(0,(uint8_t *)buffer,length);
}
void r1_goodix_native_filter_initialize(volatile struct r1_goodix_native_filter *filter,
    const float *denominator,const float *numerator,float *primary,float *secondary,
    uint32_t count,float scale)
{
    filter->numerator=numerator;
    filter->denominator=denominator;
    filter->primary=primary;
    filter->secondary=secondary;
    filter->count=count;
    filter->scale=scale;
    uint32_t bytes=(count<<2)+4u;
    zero_bytes(primary,bytes);
    zero_bytes(secondary,bytes);
}
void r1_goodix_native_nadt_reset_fields(void *allocation,uint32_t initializing)
{
    volatile struct r1_goodix_native_nadt_state *s=&r1_goodix_native_nadt_state;
    struct r1_goodix_native_nadt_workspace *w=&r1_goodix_native_nadt_workspace;
    s->values[0]=0;
    s->values[1]=0;
    if (initializing) s->allocation=allocation;
    s->flags[1]=0;
    if (initializing) { s->values[2]=0; s->values[3]=255; }
    s->counters[2]=0;
    s->flags[0xa]=0;
    s->counters[3]=0;
    zero_bytes(w->first,sizeof(w->first));
    zero_bytes(w->second,sizeof(w->second));
    zero_bytes(w->small,sizeof(w->small));
    zero_bytes(w->third,sizeof(w->third));
    zero_bytes(w->final,sizeof(w->final));
    r1_goodix_native_filter_initialize(&w->filter,r1_goodix_native_nadt_denominator,
        r1_goodix_native_nadt_numerator,w->primary,w->secondary,3,4001.0f);
    s->counters[0]=0;
    s->flags[4]=0;
    s->flags[5]=0;
    s->flags[6]=0;
    s->flags[7]=0;
    s->flags[8]=0;
    s->counters[1]=0;
    s->flags[9]=50;
    s->flags[0xb]=0;
    s->values[4]=0;
    s->flags[0xc]=0;
    s->values[5]=0;
    for (uint32_t i=0;i<8;i++) ((volatile uint32_t *)w->history)[i]=0;
    s->values[6]=0;
    s->flags[0xd]=0;
    for (uint32_t i=8;i<16;i++) ((volatile uint32_t *)w->history)[i]=0;
    s->flags[0xe]=0;
    s->flags[0xf]=0;
    s->values[7]=0;
    s->counters[4]=0;
    s->counters[5]=0;
    s->values[8]=0;
    s->values[9]=0;
    s->flags[0x10]=0;
    s->flags[0x11]=0;
    s->flags[0x12]=0;
    s->flags[0x13]=0;
    s->flags[0x15]=0;
    s->flags[0x14]=0;
    s->flags[0x17]=0;
    s->flags[0x16]=0;
    s->flags[0x18]=0;
    s->flags[3]=0;
}
goodix_nadt_ret goodix_nadt_deinit(void)
{
    volatile struct r1_goodix_native_nadt_state *s=&r1_goodix_native_nadt_state;
    r1_goodix_native_nadt_reset_fields(NULL,0);
    goodix_mem_free(s->allocation);
    s->flags[0]=0xbf;
    return GX_ALGO_NADT_SUCCESS;
}
