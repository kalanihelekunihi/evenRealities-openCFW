#include "wsf_types.h"
#include <stddef.h>
#include "wsf_timer.h"
_Static_assert(offsetof(wsfTimer_t, pNext) == 0, "pNext offset");
_Static_assert(offsetof(wsfTimer_t, ticks) == 4, "ticks offset");
_Static_assert(offsetof(wsfTimer_t, msg) == 8, "msg offset");
_Static_assert(offsetof(wsfTimer_t, handlerId) == 12, "handlerId offset");
_Static_assert(offsetof(wsfTimer_t, isStarted) == 13, "isStarted offset");
_Static_assert(sizeof(wsfTimer_t) == 16, "timer size");
