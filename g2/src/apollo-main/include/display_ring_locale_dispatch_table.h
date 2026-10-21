#ifndef OPENCFW_DISPLAY_RING_LOCALE_DISPATCH_TABLE_H
#define OPENCFW_DISPLAY_RING_LOCALE_DISPATCH_TABLE_H

#include <stddef.h>
#include <stdint.h>

typedef uint32_t (*audio_uart_locale_character_fn)(uint32_t);
typedef struct {
    uintptr_t prefix[8];
    audio_uart_locale_character_fn space;
    uintptr_t after_space;
    audio_uart_locale_character_fn lower;
} audio_uart_locale_dispatch_table;

extern volatile audio_uart_locale_dispatch_table audio_uart_ring_locale_dispatch_200044c0;

_Static_assert(sizeof(audio_uart_locale_dispatch_table) == 44,
               "selected locale table extent");
_Static_assert(offsetof(audio_uart_locale_dispatch_table, space) == 0x20,
               "locale space slot");
_Static_assert(offsetof(audio_uart_locale_dispatch_table, lower) == 0x28,
               "locale lower slot");

#endif
