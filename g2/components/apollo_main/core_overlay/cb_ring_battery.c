/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the G2 ring-battery callback facade. Stock
 * EasyLogger calls in the null-registration branch are diagnostic-only and
 * omitted; callback-list and forwarding behavior are preserved.
 */

#include <stdint.h>

#if !defined(OPEN_CFW_CB_RING_BAT_FORWARD_ONLY) && \
    !defined(OPEN_CFW_CB_RING_BAT_INIT_ONLY) && \
    !defined(OPEN_CFW_CB_RING_BAT_DEINIT_ONLY) && \
    !defined(OPEN_CFW_CB_RING_BAT_REGISTER_ONLY) && \
    !defined(OPEN_CFW_CB_RING_BAT_NOTIFY_ONLY)
#define OPEN_CFW_CB_RING_BAT_ALL 1
#endif

#ifndef OPEN_CFW_CB_RING_BAT_LIST
#define OPEN_CFW_CB_RING_BAT_LIST ((void *)(uintptr_t)0x20073f90u)
#endif
#ifndef OPEN_CFW_CB_RING_BAT_TYPE
#define OPEN_CFW_CB_RING_BAT_TYPE ((const char *)(uintptr_t)0x0075e590u)
#endif

#ifndef OPEN_CFW_CB_RING_BAT_CONSUMER
void open_cfw_retained_ring_battery_consumer(uint32_t event, uint32_t *value);
#define OPEN_CFW_CB_RING_BAT_CONSUMER(event, value) \
    open_cfw_retained_ring_battery_consumer((event), (value))
#endif
#ifndef OPEN_CFW_CALLBACK_LIST_INIT
uint32_t open_cfw_callback_mgr_init(void *list, const char *type);
#define OPEN_CFW_CALLBACK_LIST_INIT(list, type) \
    open_cfw_callback_mgr_init((list), (type))
#endif
#ifndef OPEN_CFW_CALLBACK_LIST_DEINIT
void open_cfw_callback_mgr_deinit(void *list);
#define OPEN_CFW_CALLBACK_LIST_DEINIT(list) open_cfw_callback_mgr_deinit((list))
#endif
#ifndef OPEN_CFW_CALLBACK_REGISTER
uint32_t open_cfw_callback_mgr_register(void *list, uintptr_t callback);
#define OPEN_CFW_CALLBACK_REGISTER(list, callback) \
    open_cfw_callback_mgr_register((list), (callback))
#endif
#ifndef OPEN_CFW_CALLBACK_NOTIFY
void open_cfw_callback_mgr_notify(void *list, uint32_t event, uintptr_t value);
#define OPEN_CFW_CALLBACK_NOTIFY(list, event, value) \
    open_cfw_callback_mgr_notify((list), (event), (uintptr_t)(value))
#endif

#if defined(OPEN_CFW_CB_RING_BAT_ALL) || \
    defined(OPEN_CFW_CB_RING_BAT_FORWARD_ONLY)
void open_cfw_cb_ring_battery_forward(uint32_t event, uint32_t *value)
{
    OPEN_CFW_CB_RING_BAT_CONSUMER(event, value);
}
#endif

#if defined(OPEN_CFW_CB_RING_BAT_ALL) || \
    defined(OPEN_CFW_CB_RING_BAT_INIT_ONLY)
void open_cfw_cb_ring_battery_init(void)
{
    (void)OPEN_CFW_CALLBACK_LIST_INIT(OPEN_CFW_CB_RING_BAT_LIST,
        OPEN_CFW_CB_RING_BAT_TYPE);
}
#endif

#if defined(OPEN_CFW_CB_RING_BAT_ALL) || \
    defined(OPEN_CFW_CB_RING_BAT_DEINIT_ONLY)
void open_cfw_cb_ring_battery_deinit(void)
{
    OPEN_CFW_CALLBACK_LIST_DEINIT(OPEN_CFW_CB_RING_BAT_LIST);
}
#endif

#if defined(OPEN_CFW_CB_RING_BAT_ALL) || \
    defined(OPEN_CFW_CB_RING_BAT_REGISTER_ONLY)
uint32_t open_cfw_cb_ring_battery_register(uintptr_t callback)
{
    if (callback == (uintptr_t)0u) {
        return 0u;
    }
    return OPEN_CFW_CALLBACK_REGISTER(OPEN_CFW_CB_RING_BAT_LIST, callback);
}
#endif

#if defined(OPEN_CFW_CB_RING_BAT_ALL) || \
    defined(OPEN_CFW_CB_RING_BAT_NOTIFY_ONLY)
uint32_t open_cfw_cb_ring_battery_notify(uint32_t event, uint32_t value)
{
    OPEN_CFW_CALLBACK_NOTIFY(OPEN_CFW_CB_RING_BAT_LIST, event, &value);
    return value;
}
#endif
