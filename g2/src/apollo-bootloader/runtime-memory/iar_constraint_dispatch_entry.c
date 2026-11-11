/* SPDX-License-Identifier: MIT
 * Stock IAR constraint-dispatch entry. */
#include <stdint.h>

extern uint32_t opencfw_boot_constraint_dispatch_core(const char *message);

uint32_t opencfw_boot_constraint_dispatch(const char *message)
{
    return opencfw_boot_constraint_dispatch_core(message);
}
