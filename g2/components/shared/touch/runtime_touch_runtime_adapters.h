/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_RUNTIME_ADAPTERS_H
#define OPENCFW_TOUCH_RUNTIME_ADAPTERS_H

#include <stddef.h>
#include <stdint.h>

typedef void (*open_cfw_touch_void_fn)(void);
typedef void (*open_cfw_touch_halt_fn)(int code, void *context);

enum {
    OPEN_CFW_TOUCH_RUNTIME_OK = 0,
    OPEN_CFW_TOUCH_RUNTIME_UNAVAILABLE = -1,
    OPEN_CFW_TOUCH_RUNTIME_INVALID = -2,
};

int open_cfw_touch_runtime_init_arrays(
    const open_cfw_touch_void_fn *pre_begin,
    const open_cfw_touch_void_fn *pre_end,
    const open_cfw_touch_void_fn *init_begin,
    const open_cfw_touch_void_fn *init_end);
int open_cfw_touch_runtime_exit_adapter(
    int code, open_cfw_touch_void_fn fini_hook,
    open_cfw_touch_halt_fn halt_hook, void *context);
void open_cfw_touch_runtime_init_stub(void);
void open_cfw_touch_runtime_fini_stub(void);

#endif
