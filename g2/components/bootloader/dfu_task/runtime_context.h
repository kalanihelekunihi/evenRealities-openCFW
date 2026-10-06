/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_DFU_RUNTIME_CONTEXT_H
#define OPENCFW_BOOT_DFU_RUNTIME_CONTEXT_H

#include <stdint.h>

/* Private stock helper at 0x0042d88a. */
uint32_t opencfw_boot_dfu_runtime_context_get(void);

/* Stock wrapper at 0x0042dd68. The orchestrator ignores R0, but the wrapper
 * preserves its incoming R7 value as the returned R0 value. */
void opencfw_boot_dfu_runtime_context(void);

#endif
