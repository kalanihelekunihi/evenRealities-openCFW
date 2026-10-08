#ifndef CASE_EVENT_FLAGS_OFFLINE_H
#define CASE_EVENT_FLAGS_OFFLINE_H
#include <stdint.h>
/* Coherent event handle required by kernel child providers; accepts low24 bits. */
uint32_t case_event_flags_set(void *id,uint32_t flags);
#endif
