#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Authenticated cold-zero RW pointer word @20007c4c. The pointed-to context
 * and its allocator/initialization are not reconstructed by this unit. */
volatile uint32_t r1_gomore_native_context
    __attribute__((section(".r1.gomore.native.context"),aligned(4)))=0;
extern void __aeabi_memclr(void *,size_t);
/* Native selector 0x72572 writes all 32 output bytes on every return. */
extern void r1_gomore_sleep_interval_select_native(volatile void *,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_packed_sleep_output_native(uint32_t,uint32_t,volatile void *,volatile uint32_t *,volatile void *);
struct __attribute__((packed,may_alias)) dispatch_word { uint32_t value; };

uint32_t r1_gomore_sleep_interval_dispatch_native(volatile uint32_t *count,volatile void *workspace)
{
    _Alignas(8) struct {
        volatile uint8_t source[32];
        volatile uint8_t copy[32];
    } records;
    __aeabi_memclr((void *)records.copy,32);
    uint32_t context=r1_gomore_native_context;
    r1_gomore_sleep_interval_select_native(records.source,context+4400u,context+400u,context+396u);
    memcpy((void *)records.copy,(const void *)records.source,32);
    if (!records.copy[26]) return UINT32_MAX;
    volatile struct dispatch_word *payload=(volatile struct dispatch_word *)
        ((volatile uint8_t *)workspace+8);
    uint32_t saved=payload->value;
    context=r1_gomore_native_context;
    uint32_t status=r1_gomore_packed_sleep_output_native(
        context+5112u,context+436u,records.copy,count,workspace);
    payload->value=saved;
    return status ? UINT32_MAX : 0;
}
