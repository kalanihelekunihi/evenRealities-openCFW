#include "am_mcu_apollo.h"

_Static_assert(sizeof(am_hal_mspi_dev_config_t) == 52u,
               "pinned public device config ABI changed");
_Static_assert(sizeof(am_hal_mspi_xip_config_t) == 20u,
               "pinned public XIP config ABI changed");

unsigned char opencfw_public_mspi_dev_config_size[sizeof(am_hal_mspi_dev_config_t)];
unsigned char opencfw_public_mspi_xip_config_size[sizeof(am_hal_mspi_xip_config_t)];
