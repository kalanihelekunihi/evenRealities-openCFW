#ifndef R1_SECURITY_CORDIO_H
#define R1_SECURITY_CORDIO_H

#include <stdbool.h>
#include <stdint.h>

/* The DM event type is passed opaquely across the source units; the
 * implementation includes Cordio's declaration. */
bool r1_cordio_security_dm_event(const void *event);
void r1_cordio_security_reset(uint8_t conn_id);

#endif
