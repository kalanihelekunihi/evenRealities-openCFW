#ifndef OPEN_CFW_AM_UTIL_DEBUG_SHIM_H
#define OPEN_CFW_AM_UTIL_DEBUG_SHIM_H

#include "am_util_stdio.h"

#define am_util_debug_printf(...) am_util_stdio_printf(__VA_ARGS__)

#endif
