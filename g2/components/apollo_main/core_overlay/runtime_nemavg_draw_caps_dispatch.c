/* SPDX-License-Identifier: MIT */
#include <stdint.h>

/*
 * Source-owned coordinator for Think Silicon NemaVG draw_caps().  The public
 * Apollo5 archive's DWARF fixes the source declaration at nema_vg.c:1924 and
 * the no-argument ABI.  The stock G2 body independently fixes the context
 * pointer cell and the two error-state words cleared by the NemaVG error
 * propagation macro.
 *
 * The endpoint renderers remain explicit retained providers.  Keeping those
 * dependencies visible prevents this bounded coordinator from being mistaken
 * for source ownership of draw_start_cap() or draw_end_cap().
 */

#ifndef OPEN_CFW_NEMAVG_CONTEXT_CELL
#define OPEN_CFW_NEMAVG_CONTEXT_CELL \
    ((uint8_t *const volatile *)(uintptr_t)UINT32_C(0x20074F04))
#endif

uint32_t open_cfw_retained_nemavg_draw_start_cap(void);
uint32_t open_cfw_retained_nemavg_draw_end_cap(void);
void open_cfw_retained_nemavg_set_error(uint32_t error);

#ifndef OPEN_CFW_NEMAVG_DRAW_START_CAP
#define OPEN_CFW_NEMAVG_DRAW_START_CAP \
    open_cfw_retained_nemavg_draw_start_cap
#endif
#ifndef OPEN_CFW_NEMAVG_DRAW_END_CAP
#define OPEN_CFW_NEMAVG_DRAW_END_CAP \
    open_cfw_retained_nemavg_draw_end_cap
#endif
#ifndef OPEN_CFW_NEMAVG_SET_ERROR
#define OPEN_CFW_NEMAVG_SET_ERROR open_cfw_retained_nemavg_set_error
#endif

#define OPEN_CFW_NEMAVG_CONTEXT_ERROR_WORD_0 UINT32_C(0x114)
#define OPEN_CFW_NEMAVG_CONTEXT_ERROR_WORD_1 UINT32_C(0x118)
#define OPEN_CFW_NEMAVG_INVALID_CAP_STYLE UINT32_C(0x00800000)

static __attribute__((always_inline)) inline uint32_t
open_cfw_nemavg_propagate_cap_error(uint32_t error)
{
    uint8_t *context = *OPEN_CFW_NEMAVG_CONTEXT_CELL;

    if (context != (uint8_t *)0) {
        *(uint32_t *)(void *)(context + OPEN_CFW_NEMAVG_CONTEXT_ERROR_WORD_0) =
            0U;
        *(uint32_t *)(void *)(context + OPEN_CFW_NEMAVG_CONTEXT_ERROR_WORD_1) =
            0U;
    }
    OPEN_CFW_NEMAVG_SET_ERROR(error);
    return error;
}

__attribute__((used, noinline))
uint32_t open_cfw_nemavg_draw_caps_dispatch(void)
{
    uint32_t result = OPEN_CFW_NEMAVG_DRAW_START_CAP();

    if (result != 0U)
        return open_cfw_nemavg_propagate_cap_error(result);
    result = OPEN_CFW_NEMAVG_DRAW_END_CAP();
    if (result != 0U)
        return open_cfw_nemavg_propagate_cap_error(result);
    return 0U;
}
