/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS missed-yield ABI for the Even Realities G2 Apollo-main
 * image.  The recovered scheduler state seam is kept explicit so the
 * source-owned leaf is independently extractable and relocation-free.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_MISSED_YIELD_H
#define OPEN_CFW_RUNTIME_FREERTOS_MISSED_YIELD_H

typedef __INT32_TYPE__ open_cfw_freertos_base_type;

enum {
    OPEN_CFW_FREERTOS_YIELD_PENDING_ADDRESS = 0x20074A44U,
    OPEN_CFW_FREERTOS_TRUE = 1
};

_Static_assert(
    sizeof(open_cfw_freertos_base_type) == 4U,
    "G2 FreeRTOS BaseType_t width changed"
);

#ifndef OPEN_CFW_FREERTOS_YIELD_PENDING_WORD
#define OPEN_CFW_FREERTOS_YIELD_PENDING_WORD \
    (*(volatile open_cfw_freertos_base_type *) \
        (__UINTPTR_TYPE__)OPEN_CFW_FREERTOS_YIELD_PENDING_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_YIELD_PENDING_STORE
#define OPEN_CFW_FREERTOS_YIELD_PENDING_STORE(value) \
    (OPEN_CFW_FREERTOS_YIELD_PENDING_WORD = (value))
#endif

void open_cfw_freertos_task_missed_yield(void);

#endif
