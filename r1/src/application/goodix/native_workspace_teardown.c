#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
extern uint32_t r1_goodix_native_release_cell(volatile uint32_t *);
/* The record's owned allocation is at +4, not in its first word.
 * Native calls release even for a null allocation and leaves the cell. */
void r1_goodix_native_release_record(void *record)
{
    uint32_t allocation=*(const volatile uint32_t *)((uintptr_t)record+4u);
    goodix_mem_free((void *)(uintptr_t)allocation);
}
uint32_t r1_goodix_native_workspace_destroy(void *workspace)
{
    uintptr_t base=(uintptr_t)workspace;
    static const uint16_t records[]={0x04,0x14,0x24,0x34,0x44,0x54,0x64,0x84,0x74};
    static const uint16_t cells[]={0x94,0x9c,0xa4,0xac,0xb4,0xbc,0xc4,0xcc,0xd4,
                                  0xdc,0xec,0xfc,0x10c,0x11c,0x12c,0x13c};
    for (uint32_t i=0;i<sizeof(records)/sizeof(records[0]);i++)
        r1_goodix_native_release_record((void *)(base+records[i]));
    for (uint32_t i=0;i<sizeof(cells)/sizeof(cells[0]);i++)
        (void)r1_goodix_native_release_cell((volatile uint32_t *)(base+cells[i]));
    return 0;
}
