/* Apollo GPU image binding and format stride, native 0x4b1608..0x4b178b. */
#include <stdint.h>

extern volatile uint32_t audio_uart_ambiq_unit_cell[1];
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t words);

static uint32_t align_four_native(uint32_t value)
{
    uint32_t const sum = value + 3u;
    uint32_t const correction = (uint32_t)((int32_t)sum >> 1) >> 30;
    return (sum + correction) & ~3u;
}

static uint32_t align_two_native(uint32_t value)
{
    uint32_t const sum = value + 1u;
    return (sum + (sum >> 31)) & ~1u;
}

static uint32_t divide_eight_native(uint32_t value)
{
    uint32_t const sum = value + 7u;
    uint32_t const correction = (uint32_t)((int32_t)sum >> 2) >> 29;
    return (uint32_t)((int32_t)(sum + correction) >> 3);
}

static uint32_t format_stride(uint32_t width, uint32_t format, uint32_t flags)
{
    uint32_t const kind = format & 0x7fu;
    uint32_t stride = width;
    if (flags & 0x10u) stride = align_four_native(stride);
    if (kind == 0x12u || kind == 0x16u || kind == 0x17u || kind == 0x4eu)
        stride = align_four_native(stride);
    if (kind == 0x4cu || kind == 0x4du)
        stride = align_two_native(stride);

    switch (kind) {
    case 0x0b: case 0x0c: case 0x27: case 0x2a:
        return divide_eight_native(stride);
    case 0x12:
        return stride << 1;
    case 0x16: case 0x17: case 0x4c: case 0x4d: case 0x4e:
        return stride * 3u;
    case 0x28: case 0x2b: case 0x30: case 0x31:
        return divide_eight_native(stride * 2u);
    case 0x29: case 0x2c: case 0x34: case 0x35:
        return divide_eight_native(stride * 4u);
    default:
        break;
    }

    uint32_t bytes = 4u;
    switch (kind) {
    case 4: case 5: case 6: case 0x0d: case 0x13: case 0x1d:
    case 0x3d: case 0x3e: case 0x3f: case 0x44: case 0x46:
    case 0x47: case 0x48: case 0x49: case 0x4a: case 0x4b:
        bytes = 2u;
        break;
    case 7: case 8: case 9: case 0x18: case 0x19: case 0x1a:
    case 0x38: case 0x40: case 0x41: case 0x42: case 0x43: case 0x45:
        bytes = 1u;
        break;
    case 0x39: case 0x3c:
        bytes = 3u;
        break;
    default:
        break;
    }
    return stride * bytes;
}

void display_driver_gpu_blit_4b1608(void *pixels, uint32_t width,
                                      uint32_t height, uint32_t format,
                                      uint32_t stride, uint32_t flags)
{
    if (stride == UINT32_MAX) stride = format_stride(width, format, flags);
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
    uint32_t const descriptor = (stride & 0xffffu) | (flags << 16) | (format << 24);
    *(volatile uint32_t *)(void *)(state + 0x5cu) = descriptor;
    *(volatile uint32_t *)(void *)(state + 0x50u) = (uint32_t)(uintptr_t)pixels;
    *(volatile uint32_t *)(void *)(state + 0x54u) = width;
    *(volatile uint32_t *)(void *)(state + 0x58u) = height;
    *(volatile uint32_t *)(void *)(state + 0x60u) = 1u;
    *(volatile uint32_t *)(void *)(state + 0x64u) = format;

    uint32_t *const command = audio_uart_nema_cl_get_space_514aec(3u);
    if (command == 0) return;
    command[0] = 0x10u;
    command[1] = (uint32_t)(uintptr_t)pixels;
    command[2] = 0x14u;
    command[3] = *(volatile uint32_t *)(void *)(state + 0x5cu);
    command[4] = 0x18u;
    command[5] = width | (height << 16);
}
