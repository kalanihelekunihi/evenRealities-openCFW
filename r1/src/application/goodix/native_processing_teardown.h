#ifndef R1_GOODIX_NATIVE_PROCESSING_TEARDOWN_H
#define R1_GOODIX_NATIVE_PROCESSING_TEARDOWN_H
#include <stdint.h>
#include "../../vendor/goodix_primitives/goodix_primitives.h"
/* Canonical owners shared with future native processing initialization. */
extern void *volatile r1_goodix_native_processing_context;
extern void *volatile r1_goodix_native_processing_workspace[4];
uint32_t r1_goodix_native_processing_destroy(void);
/* Requires a valid record with native type 0, 1, 2 or 6. */
void r1_goodix_native_record_dispatch_destroy(void *record);
/* Borrow the allocations created by goodix_hba_init. The caller must not
 * release either pointer; goodix_hba_deinit retains their ownership. */
bool r1_goodix_native_hba_context_owner_view(
    goodix_primitives_hr_context_owner *owner);
#endif
