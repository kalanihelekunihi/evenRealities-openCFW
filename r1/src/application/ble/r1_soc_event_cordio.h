#ifndef R1_SOC_EVENT_CORDIO_H
#define R1_SOC_EVENT_CORDIO_H

#include <stdbool.h>
#include <stdint.h>

/* Producer must run in task context. False means no event was queued. */
bool r1_cordio_soc_event_publish(uint32_t event_id);

#endif
