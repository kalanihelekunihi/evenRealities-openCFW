/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Apollo protected-MRAM conditional deactivation adapter matched to
 * stock entry 0x0047A5C0.
 */

#ifndef OPEN_CFW_MRAM_DEACTIVATE_IF_UNCONFIRMED
#define OPEN_CFW_MRAM_DEACTIVATE_IF_UNCONFIRMED(record) \
    open_cfw_mram_deactivate_record(record)
#endif

unsigned int open_cfw_mram_deactivate_record(
    unsigned char *
);

__attribute__((used, noinline))
void open_cfw_mram_deactivate_if_unconfirmed(unsigned char *record)
{
    if (record[0x30U] == 0U) {
        (void)OPEN_CFW_MRAM_DEACTIVATE_IF_UNCONFIRMED(record);
    }
}
