#ifndef R1_CORDIO_CONTROLLER_BOOTSTRAP_H
#define R1_CORDIO_CONTROLLER_BOOTSTRAP_H

#include <stdbool.h>

/* Call once after nrf_drv_clock_init, with interrupts enabled. A failed
 * attempt cannot be retried without a reset because WSF/LL state is partial.
 * The caller owns WSF dispatch and the Nordic service/event adapter. */
bool r1_cordio_controller_bootstrap(void);

#endif
