/* Original four-argument status wait under its clock and transition names. */
#include "../../hal/clock/clock/clock-timing/timing.c"

__asm__(".global stock_wait_status\n.set stock_wait_status, audio_wait4\n"
        ".global stock_delay_status\n.set stock_delay_status, audio_wait4\n"
        ".global am_hal_delay_us\n.set am_hal_delay_us, audio_delay_us\n"
        ".global codec_wrapper_delay\n.set codec_wrapper_delay, audio_delay_us\n"
        ".global stock_delay\n.set stock_delay, audio_delay_us\n"
        ".global stock_delay_us\n.set stock_delay_us, audio_delay_us\n"
        ".global uart_delay_boundary\n.set uart_delay_boundary, audio_delay_us\n");
