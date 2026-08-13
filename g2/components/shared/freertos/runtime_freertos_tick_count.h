/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS tick-count ABI for the Even Realities G2 Apollo-main
 * image.  The public leaves use a function seam so their only target
 * relocation is an authenticated Thumb branch to the separately placeable
 * xTickCount provider.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TICK_COUNT_H
#define OPEN_CFW_RUNTIME_FREERTOS_TICK_COUNT_H

typedef __UINT32_TYPE__ open_cfw_freertos_tick_type;

enum {
    OPEN_CFW_FREERTOS_TICK_COUNT_ADDRESS = 0x20074A34U
};

_Static_assert(
    sizeof(open_cfw_freertos_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);

#ifndef OPEN_CFW_FREERTOS_TICK_COUNT_WORD
#define OPEN_CFW_FREERTOS_TICK_COUNT_WORD \
    (*(volatile open_cfw_freertos_tick_type *) \
        (__UINTPTR_TYPE__)OPEN_CFW_FREERTOS_TICK_COUNT_ADDRESS)
#endif

open_cfw_freertos_tick_type open_cfw_freertos_tick_count_read(void);

#ifndef OPEN_CFW_FREERTOS_TICK_COUNT_READ
#define OPEN_CFW_FREERTOS_TICK_COUNT_READ() \
    open_cfw_freertos_tick_count_read()
#endif

open_cfw_freertos_tick_type
open_cfw_freertos_task_get_tick_count(void);

open_cfw_freertos_tick_type
open_cfw_freertos_task_get_tick_count_from_isr(void);

#endif
