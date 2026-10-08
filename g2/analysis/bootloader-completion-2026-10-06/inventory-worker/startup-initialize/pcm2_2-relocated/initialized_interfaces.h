/* SPDX-License-Identifier: MIT
 * Address-derived interface for bounded reconstruction, not whole firmware ABI.
 */
#ifndef OPENCFW_INITIALIZED_INTERFACES_H
#define OPENCFW_INITIALIZED_INTERFACES_H
#include <stdint.h>
#define OPENCFW_LOCKED_DATA_DESTINATION UINT32_C(0x20000000)
#define OPENCFW_LOCKED_DATA_BYTES UINT32_C(1371)
#define OPENCFW_LOCKED_SEQUENCE_TABLE UINT32_C(0x20000158)
#define OPENCFW_LOCKED_SEQUENCE_COUNT UINT32_C(27)
void opencfw_boot_install_initialized_data(void);
uint32_t opencfw_boot_selector_source_mask(void);
/* Returns the next scatter record; static_base is the original R9 value. */
uint32_t *opencfw_boot_expand_locked_data_record(uint32_t *record,
                                               uint32_t static_base);
#endif
