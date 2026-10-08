#ifndef CASE_CONSUMER_H
#define CASE_CONSUMER_H
#include "../deferred_event_offline/deferred.h"
/* Valid coherent queue and empty sender wait list, nonblocking only. */
int32_t case_receive_nowait(case_queue *,void *);
/* Contract: queued messages all have negative command IDs. Timer commands excluded. */
void case_drain_negative_callbacks(void);
#endif
