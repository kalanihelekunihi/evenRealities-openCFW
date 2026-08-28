/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Apollo protected-MRAM record deactivation adapter matched to
 * stock entry 0x0047A47C.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_deactivate_uintptr;

typedef unsigned int (*open_cfw_mram_deactivate_verify_function)(
    const unsigned char *
);

#ifndef OPEN_CFW_MRAM_DEACTIVATE_UPDATE
#define OPEN_CFW_MRAM_DEACTIVATE_UPDATE(record) \
    open_cfw_mram_app_db_update(record)
#endif
#ifndef OPEN_CFW_MRAM_DEACTIVATE_VERIFY
#define OPEN_CFW_MRAM_DEACTIVATE_VERIFY(record) \
    (((open_cfw_mram_deactivate_verify_function) \
        (open_cfw_mram_deactivate_uintptr)0x0047B731U)(record))
#endif

unsigned int open_cfw_mram_app_db_update(
    const unsigned char *
);

__attribute__((used, noinline))
unsigned int open_cfw_mram_deactivate_record(unsigned char *record)
{
    record[0x2FU] = 0U;
    record[0x30U] = 0U;
    (void)OPEN_CFW_MRAM_DEACTIVATE_UPDATE(record);
    return OPEN_CFW_MRAM_DEACTIVATE_VERIFY(record);
}
