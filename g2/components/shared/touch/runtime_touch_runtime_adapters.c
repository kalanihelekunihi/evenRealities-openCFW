/* SPDX-License-Identifier: MIT */
#include "runtime_touch_runtime_adapters.h"

static int valid_range(const open_cfw_touch_void_fn *begin,
                       const open_cfw_touch_void_fn *end)
{
    return (begin == NULL && end == NULL) ||
           (begin != NULL && end != NULL && end >= begin);
}

int open_cfw_touch_runtime_init_arrays(
    const open_cfw_touch_void_fn *pre_begin,
    const open_cfw_touch_void_fn *pre_end,
    const open_cfw_touch_void_fn *init_begin,
    const open_cfw_touch_void_fn *init_end)
{
    const open_cfw_touch_void_fn *item;
    if (!valid_range(pre_begin, pre_end) || !valid_range(init_begin, init_end)) {
        return OPEN_CFW_TOUCH_RUNTIME_INVALID;
    }
    for (item = pre_begin; item != pre_end; ++item) {
        if (*item != NULL) {
            (*item)();
        }
    }
    for (item = init_begin; item != init_end; ++item) {
        if (*item != NULL) {
            (*item)();
        }
    }
    return OPEN_CFW_TOUCH_RUNTIME_OK;
}

int open_cfw_touch_runtime_exit_adapter(
    int code, open_cfw_touch_void_fn fini_hook,
    open_cfw_touch_halt_fn halt_hook, void *context)
{
    if (halt_hook == NULL) {
        return OPEN_CFW_TOUCH_RUNTIME_UNAVAILABLE;
    }
    if (fini_hook != NULL) {
        fini_hook();
    }
    halt_hook(code, context);
    return OPEN_CFW_TOUCH_RUNTIME_OK;
}

void open_cfw_touch_runtime_init_stub(void) {}
void open_cfw_touch_runtime_fini_stub(void) {}
