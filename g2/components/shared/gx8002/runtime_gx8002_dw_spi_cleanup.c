/* SPDX-License-Identifier: MIT */
/* Recovered pointer chain and controller word clear; other private fields unknown. */
#include <driver/spi.h>
struct open_cfw_dw_spi_private_prefix {
    unsigned int reserved;
    volatile unsigned int *registers;
};
_Static_assert(__builtin_offsetof(struct spi_master, driver_data)==24,"SPI private pointer ABI");
_Static_assert(__builtin_offsetof(struct open_cfw_dw_spi_private_prefix, registers)==4,"DW register pointer ABI");
void open_cfw_gx8002_dw_spi_cleanup(struct spi_device *device)
{
    volatile struct spi_device *d=device;
    volatile struct spi_master *master=d->master;
    volatile struct open_cfw_dw_spi_private_prefix *private=master->driver_data;
    volatile unsigned int *registers=private->registers;
    registers[2]=0;
}
