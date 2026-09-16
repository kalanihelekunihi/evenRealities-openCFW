/* SPDX-License-Identifier: MIT */
/* Reset-cleared backup SPI master; probe and registration fill its fields. */
#include <driver/spi.h>
struct spi_master open_cfw_gx8002_backup_spi_master;
_Static_assert(sizeof(struct spi_master)==36,"backup master size");
_Static_assert(__builtin_offsetof(struct spi_master,setup)==8,"setup slot");
_Static_assert(__builtin_offsetof(struct spi_master,transfer)==12,"transfer slot");
_Static_assert(__builtin_offsetof(struct spi_master,driver_data)==24,"driver state");
_Static_assert(__builtin_offsetof(struct spi_master,list)==28,"list node");
