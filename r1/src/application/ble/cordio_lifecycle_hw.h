#ifndef R1_CORDIO_LIFECYCLE_HW_H
#define R1_CORDIO_LIFECYCLE_HW_H

#include <stdbool.h>

bool r1_cordio_lfclk_is_running(void);
bool r1_cordio_sd_evt_irq_prepare(void);
void r1_cordio_hardware_shutdown(void);

#endif
