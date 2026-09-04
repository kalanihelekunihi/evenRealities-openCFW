/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room behavioral reconstruction of the G2 2.2.6.10 eAT core at
 * [0x005412E0,0x0054157A).  The authenticated behavior and fixed ABI are
 * recorded in docs/research/g2-at-core-recovery.md.  No stock instructions
 * are reproduced here.
 */

#include "at_core.h"

#include <stddef.h>

#ifndef OPEN_CFW_AT_CORE_STATE
#define OPEN_CFW_AT_CORE_STATE \
    ((struct open_cfw_at_core_state *)(uintptr_t)0x2037bf5cu)
#endif

#ifndef OPEN_CFW_AT_CORE_COMMAND_TABLE
#define OPEN_CFW_AT_CORE_COMMAND_TABLE \
    ((const struct open_cfw_at_core_command *)(uintptr_t)0x006c9260u)
#endif

#ifndef OPEN_CFW_AT_CORE_COMMAND_TABLE_END
#define OPEN_CFW_AT_CORE_COMMAND_TABLE_END \
    ((uintptr_t)0x006c93b0u)
#endif

#ifndef OPEN_CFW_AT_CORE_PARSER_BUFFER
#define OPEN_CFW_AT_CORE_PARSER_BUFFER \
    ((char *)(uintptr_t)0x2037b3c0u)
#endif

#ifndef OPEN_CFW_AT_CORE_PARSER_INIT
void open_cfw_retained_at_core_parser_init(void);
#define OPEN_CFW_AT_CORE_PARSER_INIT() \
    open_cfw_retained_at_core_parser_init()
#endif

#ifndef OPEN_CFW_AT_CORE_PARSER_NEXT
char *open_cfw_retained_at_core_parser_next(
    const char *input,
    const uint16_t *separators,
    char **cursor
);
#define OPEN_CFW_AT_CORE_PARSER_NEXT(input, separators, cursor) \
    open_cfw_retained_at_core_parser_next((input), (separators), (cursor))
#endif

#ifndef OPEN_CFW_AT_CORE_PARSER_ADAPT
void open_cfw_retained_at_core_parser_adapt(
    open_cfw_at_core_command_handler handler,
    const char *parameter_1,
    const char *parameter_2
);
#define OPEN_CFW_AT_CORE_PARSER_ADAPT(handler, parameter_1, parameter_2) \
    open_cfw_retained_at_core_parser_adapt( \
        (handler), (parameter_1), (parameter_2) \
    )
#endif

#ifndef OPEN_CFW_AT_CORE_VSNPRINTF
int open_cfw_runtime_vsnprintf_wrapper(
    unsigned char *buffer,
    unsigned int capacity,
    const unsigned char *format,
    __builtin_va_list arguments
);
#define OPEN_CFW_AT_CORE_VSNPRINTF(buffer, capacity, format, arguments) \
    open_cfw_runtime_vsnprintf_wrapper( \
        (unsigned char *)(buffer), \
        (capacity), \
        (const unsigned char *)(format), \
        (arguments) \
    )
#endif

enum {
    OPEN_CFW_AT_CORE_CALLBACK_COUNT = 3,
    OPEN_CFW_AT_CORE_SEGMENT_COUNT = 3,
    OPEN_CFW_AT_CORE_SEGMENT_CAPACITY = 256,
    OPEN_CFW_AT_CORE_PARSER_BUFFER_BYTES = 768,
    OPEN_CFW_AT_CORE_READY_MASK = 3,
    OPEN_CFW_AT_CORE_FILTER_FLAG = 1u << 2
};

#if !defined(OPEN_CFW_AT_CORE_REGISTER_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_AT_CORE_INIT_ONLY) && \
    !defined(OPEN_CFW_AT_CORE_HANDLER_ONLY) && \
    !defined(OPEN_CFW_AT_CORE_OUTPUT_ONLY) && \
    !defined(OPEN_CFW_AT_CORE_DISPATCH_COMMAND_ONLY)
#define OPEN_CFW_AT_CORE_ALL 1
#endif

#if defined(OPEN_CFW_AT_CORE_ALL) || \
    defined(OPEN_CFW_AT_CORE_DISPATCH_COMMAND_ONLY)
static __attribute__((always_inline)) inline size_t
open_cfw_at_core_string_length(const char *string)
{
    size_t length = 0;
    while (string[length] != '\0') {
        length += 1;
    }
    return length;
}

static __attribute__((always_inline)) inline int
open_cfw_at_core_memory_equal(
    const char *left,
    const char *right,
    size_t length
)
{
    size_t index;
    for (index = 0; index < length; index += 1) {
        if ((unsigned char)left[index] != (unsigned char)right[index]) {
            return 0;
        }
    }
    return 1;
}
#endif

#if defined(OPEN_CFW_AT_CORE_ALL) || defined(OPEN_CFW_AT_CORE_HANDLER_ONLY)
static __attribute__((always_inline)) inline void
open_cfw_at_core_copy_segment(char *destination, const char *source)
{
    size_t index = 0;
    while (
        index + 1u < OPEN_CFW_AT_CORE_SEGMENT_CAPACITY
        && source[index] != '\0'
    ) {
        destination[index] = source[index];
        index += 1;
    }
    destination[index] = '\0';
}
#endif

#if defined(OPEN_CFW_AT_CORE_ALL) || \
    defined(OPEN_CFW_AT_CORE_REGISTER_CALLBACK_ONLY)
void open_cfw_at_core_register_callback(
    uint8_t index,
    open_cfw_at_core_output_callback callback
)
{
    struct open_cfw_at_core_state *state = OPEN_CFW_AT_CORE_STATE;
    if (index < OPEN_CFW_AT_CORE_CALLBACK_COUNT) {
        state->callbacks[index] = callback;
        state->callback_mask |= 1u << index;
    }
}
#endif

#if defined(OPEN_CFW_AT_CORE_ALL) || defined(OPEN_CFW_AT_CORE_INIT_ONLY)
void open_cfw_at_core_init(void)
{
    struct open_cfw_at_core_state *state = OPEN_CFW_AT_CORE_STATE;
    state->commands = OPEN_CFW_AT_CORE_COMMAND_TABLE;
    state->command_count = (uint32_t)(
        (OPEN_CFW_AT_CORE_COMMAND_TABLE_END
         - (uintptr_t)OPEN_CFW_AT_CORE_COMMAND_TABLE)
        / sizeof(struct open_cfw_at_core_command)
    );
    OPEN_CFW_AT_CORE_PARSER_INIT();
    state->reserved = 0;
    state->flags |= OPEN_CFW_AT_CORE_READY_MASK;
}
#endif

#if defined(OPEN_CFW_AT_CORE_ALL) || defined(OPEN_CFW_AT_CORE_HANDLER_ONLY)
void open_cfw_at_core_handler(const char *command)
{
    char *buffer = OPEN_CFW_AT_CORE_PARSER_BUFFER;
    const uint16_t separator = (uint16_t)'=';
    char *cursor = NULL;
    char *segment;
    uint8_t count = 0;
    size_t index;

    for (index = 0; index < OPEN_CFW_AT_CORE_PARSER_BUFFER_BYTES; index += 1) {
        buffer[index] = '\0';
    }
    segment = OPEN_CFW_AT_CORE_PARSER_NEXT(command, &separator, &cursor);
    while (segment != NULL && count < OPEN_CFW_AT_CORE_SEGMENT_COUNT) {
        open_cfw_at_core_copy_segment(
            buffer + (size_t)count * OPEN_CFW_AT_CORE_SEGMENT_CAPACITY,
            segment
        );
        count += 1;
        segment = OPEN_CFW_AT_CORE_PARSER_NEXT(NULL, &separator, &cursor);
    }
    open_cfw_at_core_dispatch_command(
        buffer,
        count >= 2u ? buffer + OPEN_CFW_AT_CORE_SEGMENT_CAPACITY : NULL,
        count >= 3u ? buffer + 2u * OPEN_CFW_AT_CORE_SEGMENT_CAPACITY : NULL
    );
}
#endif

#if defined(OPEN_CFW_AT_CORE_ALL) || defined(OPEN_CFW_AT_CORE_OUTPUT_ONLY)
void open_cfw_at_core_output(const char *format, ...)
{
    struct open_cfw_at_core_state *state = OPEN_CFW_AT_CORE_STATE;
    __builtin_va_list arguments;
    int length;
    uint32_t index;

    __builtin_va_start(arguments, format);
    length = OPEN_CFW_AT_CORE_VSNPRINTF(
        state->output,
        sizeof(state->output),
        format,
        arguments
    );
    __builtin_va_end(arguments);
    if (length <= 0) {
        return;
    }

    if (state->output_mode == 0u) {
        for (index = 1; index < OPEN_CFW_AT_CORE_CALLBACK_COUNT; index += 1) {
            if (
                (state->callback_mask & (1u << index)) != 0u
                && state->callbacks[index] != NULL
            ) {
                state->callbacks[index](state->output, length);
            }
        }
    }
    else if (
        state->output_mode < OPEN_CFW_AT_CORE_CALLBACK_COUNT
        && (state->callback_mask & (1u << state->output_mode)) != 0u
        && state->callbacks[state->output_mode] != NULL
    ) {
        state->callbacks[state->output_mode](state->output, length);
    }
}
#endif

#if defined(OPEN_CFW_AT_CORE_ALL) || \
    defined(OPEN_CFW_AT_CORE_DISPATCH_COMMAND_ONLY)
void open_cfw_at_core_dispatch_command(
    const char *command,
    const char *parameter_1,
    const char *parameter_2
)
{
    struct open_cfw_at_core_state *state = OPEN_CFW_AT_CORE_STATE;
    size_t command_length;
    uint32_t index;

    if (
        (state->flags & OPEN_CFW_AT_CORE_READY_MASK)
            != OPEN_CFW_AT_CORE_READY_MASK
        || command == NULL
    ) {
        return;
    }
    command_length = open_cfw_at_core_string_length(command);
    if (command_length >= OPEN_CFW_AT_CORE_SEGMENT_CAPACITY) {
        return;
    }

    for (index = 0; index < state->command_count; index += 1) {
        const struct open_cfw_at_core_command *record =
            &state->commands[index];
        size_t name_length = open_cfw_at_core_string_length(record->name);
        if (
            name_length != command_length
            || !open_cfw_at_core_memory_equal(
                record->name, command, command_length
            )
        ) {
            continue;
        }
        if (
            (state->flags & OPEN_CFW_AT_CORE_FILTER_FLAG) != 0u
            && (record->flags & 1u) == 0u
        ) {
            return;
        }
        if (record->handler != NULL) {
            if (((record->flags & 3u) >> 1u) == 0u) {
                record->handler(parameter_1, parameter_2);
            }
            else {
                OPEN_CFW_AT_CORE_PARSER_ADAPT(
                    record->handler, parameter_1, parameter_2
                );
            }
        }
    }
}
#endif
