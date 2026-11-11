#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
#include "goodix_hba.h"
#include "native_processing_teardown.h"
#include "native_hba_calc.h"
#include "native_spo2_initialize.h"
extern void *memset(void *,int,size_t);
extern int strcmp(const char *,const char *);
extern uint32_t r1_goodix_hba_workspace_initialize(void *);
extern const void *r1_goodix_hba_table_a692c_get(void);
extern const void *r1_goodix_hba_table_a04cc_get(void);
extern const void *r1_goodix_hba_table_9d640_get(void);
extern const void *r1_goodix_hba_table_a50b0_get(void);
extern void *r1_goodix_native_graph_record_create(uint32_t *);
static uint32_t word(uintptr_t p) { return *(const volatile uint32_t *)p; }
static void put32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }
static void put16(uintptr_t p,uint16_t v) { *(volatile uint16_t *)p=v; }
static void put8(uintptr_t p,uint8_t v) { *(volatile uint8_t *)p=v; }
static uintptr_t context(void) { return (uintptr_t)r1_goodix_native_processing_context; }
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(goodix_primitives_hr_primary_context)==336,
    "native HBA primary allocation");
_Static_assert(sizeof(goodix_primitives_hr_secondary_context)==344,
    "native HBA workspace allocation");
#endif
bool r1_goodix_native_hba_context_owner_view(
    goodix_primitives_hr_context_owner *owner)
{
    if (owner==NULL || r1_goodix_native_processing_context==NULL ||
            r1_goodix_native_processing_workspace[0]==NULL) return false;
    *owner=(goodix_primitives_hr_context_owner){
        .primary=(goodix_primitives_hr_primary_context *)
            r1_goodix_native_processing_context,
        .secondary=(goodix_primitives_hr_secondary_context *)
            r1_goodix_native_processing_workspace[0]
    };
    return true;
}
uint32_t r1_goodix_hba_library_code_get(void) { return UINT32_C(0x12f9); }
uint32_t r1_goodix_native_byte_queue_initialize(void *record,void *buffer,uint32_t count)
{
    if (!buffer) buffer=goodix_mem_malloc((int32_t)count);
    uintptr_t p=(uintptr_t)record;
    put16(p+4,0);put32(p,(uint32_t)(uintptr_t)buffer);
    put16(p+6,(uint16_t)count);put16(p+8,0);
    return 0;
}
goodix_hba_ret goodix_hba_init(const void *configuration,uint32_t size,const char *interface)
{
    uintptr_t cfg=(uintptr_t)configuration;
    if (!configuration || size!=36 || strcmp(interface,"pv_v1.1.0")) return (goodix_hba_ret)1;
    r1_goodix_hba_calculation_unbind();
    void *allocation=goodix_mem_malloc(336);
    r1_goodix_native_processing_context=allocation;
    uintptr_t p=(uintptr_t)allocation;
    uint8_t mode=*(const volatile uint8_t *)cfg;
    put8(p+0x13,mode);
    uint32_t rate=word(cfg+4);if (!rate) rate=25;
    uint16_t narrow_rate=(uint16_t)rate;
    put16(p,narrow_rate);put16(p+2,(uint16_t)(narrow_rate/25u));
    int32_t minimum=(int32_t)word(cfg+8);if (minimum<=0) minimum=1;
    put8(p+0x1c,(uint8_t)minimum);
    uint32_t stride=word(cfg+0x14);if (!stride) stride=1;put32(p+0x20,stride);
    uint32_t limit=word(cfg+0x1c);if (limit>20) limit=20;put32(p+0x24,limit);
    uint32_t terminal=word(cfg+0x18);if (!terminal) terminal=202;put32(p+0x148,terminal);
    put32(p+0x28,word(cfg+0x20));put32(p+0x18,9);
    if (mode==0) put32(p+0x14,20);
    else if (mode==1) put32(p+0x14,15);
    else if (mode==2) put32(p+0x14,30);
    uint32_t window=word(cfg+0x10);if (window) put32(p+0x14,window);
    window=word(cfg+0xc);if (window) put32(p+0x18,window);
    put8(p+0xac,*(const volatile uint8_t *)(p+0x14));
    for (uint32_t i=0;i<4;i++) r1_goodix_native_processing_workspace[i]=NULL;
    allocation=goodix_mem_malloc(344);
    r1_goodix_native_processing_workspace[0]=allocation;
    (void)r1_goodix_hba_workspace_initialize(allocation);
    p=context()+0x58;
    static const uint8_t control[6]={1,5,128,1,4,1};
    for (uint32_t i=0;i<6;i++) put8(p+i,control[i]);
    put32(p+8,356);put32(p+12,2);put32(p+16,1);
    uint32_t parameters[28];(void)memset(parameters,0,sizeof(parameters));
    parameters[4]=1;parameters[8]=6;
    parameters[1]=(uint32_t)(uintptr_t)r1_goodix_hba_table_a692c_get();
    parameters[2]=r1_goodix_hba_library_code_get()<<2;
    parameters[3]=(uint32_t)(uintptr_t)r1_goodix_hba_table_a04cc_get();
    parameters[5]=(uint32_t)(uintptr_t)r1_goodix_hba_table_9d640_get();
    parameters[9]=(uint32_t)(uintptr_t)r1_goodix_hba_table_a50b0_get();
    allocation=r1_goodix_native_graph_record_create(parameters);put32(context()+0x6c,(uint32_t)(uintptr_t)allocation);
    allocation=r1_goodix_native_graph_record_create(parameters+4);put32(context()+0x70,(uint32_t)(uintptr_t)allocation);
    allocation=r1_goodix_native_graph_record_create(parameters+8);put32(context()+0x84,(uint32_t)(uintptr_t)allocation);
    put8(context()+0xad,0);
    (void)r1_goodix_native_byte_queue_initialize((void *)(context()+0xb0),NULL,3);
    (void)r1_goodix_native_float_record_initialize((void *)(context()+0xbc),NULL,3,1);
    (void)r1_goodix_native_byte_queue_initialize((void *)(context()+0xcc),NULL,3);
    (void)r1_goodix_native_float_record_initialize((void *)(context()+0xd8),NULL,3,1);
    p=context();put8(p+0x110,0);put8(p+0x111,0);put8(p+0x112,0);
    for (uint32_t i=0;i<4;i++) {
        put32(p+0x114+4*i,UINT32_C(0x48800000));
        put32(p+0x128+8*i,0);put32(p+0x12c+8*i,0);
    }
    return (goodix_hba_ret)0;
}
