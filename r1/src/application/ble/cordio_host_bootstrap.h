#ifndef R1_CORDIO_HOST_BOOTSTRAP_H
#define R1_CORDIO_HOST_BOOTSTRAP_H

#include <stdbool.h>

/* Call after controller/HCI initialization and before starting WSF dispatch. */
void r1_cordio_host_bootstrap(void);
bool r1_cordio_host_ready(void);
void r1_cordio_host_request_shutdown(void);

#endif
