/* SPDX-License-Identifier: MIT
 * Recovered diagnostic accessor; preserve the second state read after printf.
 */
#include <stdint.h>
extern int open_cfw_gx8002_printf(const char *, ...);
uint32_t open_cfw_gx8002_gsensor_workstate(void)
{
    volatile uint32_t *state = (volatile uint32_t *)(uintptr_t)0x20026c70u;
    open_cfw_gx8002_printf((const char *)(uintptr_t)0x1020adaau, (int32_t)*state);
    return *state;
}
