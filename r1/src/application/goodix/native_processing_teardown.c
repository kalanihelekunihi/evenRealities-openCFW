#include <stdint.h>
#include "goodix_mem.h"
#include "native_processing_teardown.h"
#include "native_hba_calc.h"
extern uint32_t r1_goodix_native_workspace_destroy(void *);
extern uint32_t r1_goodix_native_record_destroy(void *);
extern uint32_t r1_goodix_native_extended_record_destroy(void *);
extern uint32_t r1_goodix_native_release_nullable(void *);
extern uint32_t r1_goodix_native_release_cell(volatile uint32_t *);
void *volatile r1_goodix_native_processing_context
    __attribute__((section(".r1.goodix.native.processing.context"),aligned(4)));
void *volatile r1_goodix_native_processing_workspace[4]
    __attribute__((section(".r1.goodix.native.processing.workspace"),aligned(4)));
void r1_goodix_native_record_dispatch_destroy(void *record)
{
    typedef uint32_t (*destroy_fn)(void *);
    static const destroy_fn providers[7]={
        r1_goodix_native_extended_record_destroy,
        r1_goodix_native_record_destroy,
        r1_goodix_native_record_destroy,
        0,0,0,
        r1_goodix_native_release_nullable
    };
    uint32_t type=*(const volatile uint32_t *)record;
    (void)providers[type](record);
}
uint32_t r1_goodix_native_processing_destroy(void)
{
    r1_goodix_hba_calculation_unbind();
    (void)r1_goodix_native_workspace_destroy(r1_goodix_native_processing_workspace[0]);
    /* The stock owner is read again after teardown. Neither owner is cleared. */
    goodix_mem_free(r1_goodix_native_processing_workspace[0]);
    static const uint8_t records[]={0x6c,0x70,0x84};
    for (uint32_t i=0;i<sizeof(records);i++) {
        uintptr_t context=(uintptr_t)r1_goodix_native_processing_context;
        uint32_t record=*(const volatile uint32_t *)(context+records[i]);
        r1_goodix_native_record_dispatch_destroy((void *)(uintptr_t)record);
    }
    static const uint8_t cells[]={0xb0,0xbc,0xcc,0xd8};
    for (uint32_t i=0;i<sizeof(cells);i++)
        (void)r1_goodix_native_release_cell((volatile uint32_t *)
            ((uintptr_t)r1_goodix_native_processing_context+cells[i]));
    goodix_mem_free(r1_goodix_native_processing_context);
    return 0;
}
