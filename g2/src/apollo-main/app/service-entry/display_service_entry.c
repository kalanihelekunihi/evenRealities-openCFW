/* Native display service start 0x44227e and framebuffer-base getter 0x46ca6e. */
#include <stdint.h>
extern void audio_uart_efs_service_init_458c48(void);
extern void audio_uart_logger_cancel_ble_transmit_458e48(void);

void audio_uart_display_service_prepare(void)
{
    audio_uart_efs_service_init_458c48();
    audio_uart_logger_cancel_ble_transmit_458e48();
}

uintptr_t audio_uart_display_pixel_format(void)
{
    /* Literal at 0x46cac4 is the authenticated external framebuffer base. */
    return (uintptr_t)0x20080000u;
}
