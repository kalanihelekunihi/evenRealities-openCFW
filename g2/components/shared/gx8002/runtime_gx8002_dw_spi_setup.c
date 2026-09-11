/* SPDX-License-Identifier: MIT */
/* Reconstructed from the fully attributed stock dw_spi_setup sequence. */
#include <driver/spi.h>
typedef __UINTPTR_TYPE__ uintptr_t;
extern unsigned int open_cfw_gx8002_clock_frequency(unsigned int module);
struct open_cfw_dw_spi_device_state {
    struct spi_device *device;
    unsigned int control;
    unsigned int divider;
    unsigned int transfer_mode;
};
_Static_assert(__builtin_offsetof(struct spi_device, controller_state) == 12,
               "SPI device state ABI");
_Static_assert(sizeof(struct open_cfw_dw_spi_device_state) == 16,
               "SPI state ABI");

int open_cfw_gx8002_dw_spi_setup(struct spi_device *device)
{
    struct spi_device *d = device;
    d->mode = 0;
    if (!d->bits_per_word)
        d->bits_per_word = 8;
    struct open_cfw_dw_spi_device_state *state = d->controller_state;
    if (!state) {
        state = (void *)(uintptr_t)0x20027ae0u;
        if (state->device)
            return -12;
    }
    if (d->max_speed_hz == 0)
        d->max_speed_hz = 10000000u;
    unsigned int clock = open_cfw_gx8002_clock_frequency(14);
    unsigned int speed = d->max_speed_hz;
    unsigned int divider = clock / speed;
    /* GCC's csky_split_and selects 32-bit ANDNI before BCLRI for "& ~1u".
     * The low-register read/write constraint selects the understood 16-bit
     * instruction needed by this fixed entry's 116-byte envelope. No memory
     * or flags are changed. */
    __asm__("bclri %0, 0" : "+a" (divider));
    if (divider * speed != clock)
        divider += 2;
    state->device = device;
    unsigned int format = d->data_format;
    unsigned int mode = d->mode;
    state->control = 0x80000000u | ((format & 3u) << 22)
                     | ((mode & 3u) << 8);
    state->divider = divider;
    state->transfer_mode = 2;
    d->controller_state = (void *)state;
    return 0;
}
