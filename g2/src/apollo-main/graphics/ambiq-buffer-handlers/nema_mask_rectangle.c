/* Apollo NEMA rectangle command at native 0x522ae0, with its r0 return. */
#include <stdint.h>
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t);
extern volatile uint32_t audio_uart_nema_context_cell[1];
uint32_t audio_uart_nema_mask_rectangle_522ae0(int32_t x, int32_t y,
                                               int32_t width, int32_t height) {
    if (width < 1 || height < 1) return (uint32_t)x;
    uint32_t *command = audio_uart_nema_cl_get_space_514aec(3u);
    if (command == 0) return 0u;
    command[0] = 0x104u;
    command[1] = ((uint32_t)x & 0xffffu) | ((uint32_t)y << 16);
    command[2] = 0x108u;
    command[3] = ((uint32_t)x + (uint32_t)width) & 0xffffu;
    command[3] |= ((uint32_t)y + (uint32_t)height) << 16;
    command[4] = 0xff000100u;
    volatile uint8_t *ctx = (volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    command[5] = *(volatile uint32_t *)(void *)(ctx + 0x18u) | 2u;
    return (uint32_t)(uintptr_t)command;
}
