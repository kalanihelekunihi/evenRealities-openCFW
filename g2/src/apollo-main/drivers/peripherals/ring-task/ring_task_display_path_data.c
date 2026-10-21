#include <stdint.h>

uint8_t audio_uart_ring_thread_cb[112]
    __attribute__((section(".g2_ram_20072290"), used));
uint8_t audio_uart_ring_thread_stack[4096]
    __attribute__((section(".g2_ram_2036be40"), used));

static const char display_source_path_bytes[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\"
    "lvgl_ambiq_porting\\lv_ambiq_display.c";
const char *audio_uart_display_source_path = display_source_path_bytes;
