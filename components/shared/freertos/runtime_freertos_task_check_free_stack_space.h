/*
 * SPDX-License-Identifier: MIT
 *
 * Candidate-only FreeRTOS stack high-water helper ABI for the Even Realities
 * G2 Apollo-main image. This header fixes only the four configuration values
 * proven by focused disassembly of the official V10.5.1 helper.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_CHECK_FREE_STACK_SPACE_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_CHECK_FREE_STACK_SPACE_H

typedef __UINT8_TYPE__ open_cfw_freertos_stack_byte;
typedef __UINT16_TYPE__ open_cfw_freertos_stack_depth_type;
typedef __UINT32_TYPE__ open_cfw_freertos_stack_type;

enum {
    OPEN_CFW_FREERTOS_STACK_FILL_BYTE = 0xA5U,
    OPEN_CFW_FREERTOS_STACK_GROWTH = -1
};

_Static_assert(
    OPEN_CFW_FREERTOS_STACK_FILL_BYTE == 0xA5U,
    "FreeRTOS V10.5.1 stack fill byte changed"
);
_Static_assert(
    OPEN_CFW_FREERTOS_STACK_GROWTH == -1,
    "G2 FreeRTOS stack growth direction changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_stack_type) == 4U,
    "G2 FreeRTOS StackType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_stack_depth_type) == 2U,
    "G2 FreeRTOS configSTACK_DEPTH_TYPE width changed"
);

open_cfw_freertos_stack_depth_type
open_cfw_freertos_task_check_free_stack_space(
    const open_cfw_freertos_stack_byte *stack_byte
);

#endif
