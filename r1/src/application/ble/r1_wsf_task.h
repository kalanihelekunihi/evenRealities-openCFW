#ifndef R1_WSF_TASK_H
#define R1_WSF_TASK_H

#include <stdbool.h>
#include <stdint.h>

/* Start WSF dispatch after controller/bootstrap initialization. */
bool r1_cordio_wsf_task_start(void);
bool r1_cordio_wsf_wait_until(bool (*ready)(void), uint32_t max_ticks);
void r1_cordio_wsf_task_stop_request(void);

#endif
