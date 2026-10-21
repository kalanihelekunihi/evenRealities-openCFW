/* WSF assert and display fatal paths share native callback cell 0x2007456c. */
#include <stdint.h>

_Static_assert(sizeof(uintptr_t) == 4, "Apollo callback cell must be one word");

void (*audio_uart_display_fatal_handler)(const char *, const char *, uint32_t)
    __attribute__((section(".g2_ram_2007456c")));
extern uintptr_t audio_ble_wsf_assert_hook
    __attribute__((alias("audio_uart_display_fatal_handler")));
