/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 charge and message-count callback
 * facades.  EasyLogger calls in the stock null-callback branches are omitted
 * because they are diagnostic-only; callback-list state and return behavior
 * remain implemented through the recovered generic callback-manager ABI.
 */

#include <stdint.h>

#if !defined(OPEN_CFW_CB_CHARGE_INIT_ONLY) && \
    !defined(OPEN_CFW_CB_CHARGE_DEINIT_ONLY) && \
    !defined(OPEN_CFW_CB_CHARGE_REGISTER_ONLY) && \
    !defined(OPEN_CFW_CB_CHARGE_UNREGISTER_ONLY) && \
    !defined(OPEN_CFW_CB_CHARGE_NOTIFY_ONLY) && \
    !defined(OPEN_CFW_CB_MSG_INIT_ONLY) && \
    !defined(OPEN_CFW_CB_MSG_DEINIT_ONLY) && \
    !defined(OPEN_CFW_CB_MSG_REGISTER_ONLY) && \
    !defined(OPEN_CFW_CB_MSG_UNREGISTER_ONLY) && \
    !defined(OPEN_CFW_CB_MSG_NOTIFY_ONLY)
#define OPEN_CFW_CALLBACK_FACADES_ALL 1
#endif

#ifndef OPEN_CFW_CB_CHARGE_LIST
#define OPEN_CFW_CB_CHARGE_LIST ((void *)(uintptr_t)0x20073f78u)
#endif
#ifndef OPEN_CFW_CB_MSG_LIST
#define OPEN_CFW_CB_MSG_LIST ((void *)(uintptr_t)0x20073f84u)
#endif
#ifndef OPEN_CFW_CB_CHARGE_TYPE
#define OPEN_CFW_CB_CHARGE_TYPE ((const char *)(uintptr_t)0x0078a574u)
#endif
#ifndef OPEN_CFW_CB_MSG_TYPE
#define OPEN_CFW_CB_MSG_TYPE ((const char *)(uintptr_t)0x0078a58cu)
#endif

#ifndef OPEN_CFW_CALLBACK_LIST_INIT
void open_cfw_retained_callback_list_init(void *list, const char *type);
#define OPEN_CFW_CALLBACK_LIST_INIT(list, type) \
    open_cfw_retained_callback_list_init((list), (type))
#endif
#ifndef OPEN_CFW_CALLBACK_LIST_DEINIT
void open_cfw_retained_callback_list_deinit(void *list);
#define OPEN_CFW_CALLBACK_LIST_DEINIT(list) \
    open_cfw_retained_callback_list_deinit((list))
#endif
#ifndef OPEN_CFW_CALLBACK_REGISTER
uint32_t open_cfw_retained_callback_register(void *list, uintptr_t callback);
#define OPEN_CFW_CALLBACK_REGISTER(list, callback) \
    open_cfw_retained_callback_register((list), (callback))
#endif
#ifndef OPEN_CFW_CALLBACK_UNREGISTER
void open_cfw_retained_callback_unregister(void *list, uintptr_t callback);
#define OPEN_CFW_CALLBACK_UNREGISTER(list, callback) \
    open_cfw_retained_callback_unregister((list), (callback))
#endif
#ifndef OPEN_CFW_CALLBACK_NOTIFY
void open_cfw_retained_callback_notify(
    void *list, uint32_t event, uint32_t *value);
#define OPEN_CFW_CALLBACK_NOTIFY(list, event, value) \
    open_cfw_retained_callback_notify((list), (event), (value))
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_CHARGE_INIT_ONLY)
void open_cfw_cb_charge_init(void)
{
    OPEN_CFW_CALLBACK_LIST_INIT(OPEN_CFW_CB_CHARGE_LIST,
        OPEN_CFW_CB_CHARGE_TYPE);
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_CHARGE_DEINIT_ONLY)
void open_cfw_cb_charge_deinit(void)
{
    OPEN_CFW_CALLBACK_LIST_DEINIT(OPEN_CFW_CB_CHARGE_LIST);
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_CHARGE_REGISTER_ONLY)
uint32_t open_cfw_cb_charge_register(uintptr_t callback)
{
    if (callback == (uintptr_t)0u) {
        return 0u;
    }
    return OPEN_CFW_CALLBACK_REGISTER(OPEN_CFW_CB_CHARGE_LIST, callback);
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_CHARGE_UNREGISTER_ONLY)
void open_cfw_cb_charge_unregister(uintptr_t callback)
{
    if (callback != (uintptr_t)0u) {
        OPEN_CFW_CALLBACK_UNREGISTER(OPEN_CFW_CB_CHARGE_LIST, callback);
    }
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_CHARGE_NOTIFY_ONLY)
uint32_t open_cfw_cb_charge_notify(uint32_t event, uint32_t value)
{
    OPEN_CFW_CALLBACK_NOTIFY(OPEN_CFW_CB_CHARGE_LIST, event, &value);
    return value;
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_MSG_INIT_ONLY)
void open_cfw_cb_msg_init(void)
{
    OPEN_CFW_CALLBACK_LIST_INIT(OPEN_CFW_CB_MSG_LIST, OPEN_CFW_CB_MSG_TYPE);
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_MSG_DEINIT_ONLY)
void open_cfw_cb_msg_deinit(void)
{
    OPEN_CFW_CALLBACK_LIST_DEINIT(OPEN_CFW_CB_MSG_LIST);
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_MSG_REGISTER_ONLY)
uint32_t open_cfw_cb_msg_register(uintptr_t callback)
{
    if (callback == (uintptr_t)0u) {
        return 0u;
    }
    return OPEN_CFW_CALLBACK_REGISTER(OPEN_CFW_CB_MSG_LIST, callback);
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_MSG_UNREGISTER_ONLY)
void open_cfw_cb_msg_unregister(uintptr_t callback)
{
    if (callback != (uintptr_t)0u) {
        OPEN_CFW_CALLBACK_UNREGISTER(OPEN_CFW_CB_MSG_LIST, callback);
    }
}
#endif

#if defined(OPEN_CFW_CALLBACK_FACADES_ALL) || \
    defined(OPEN_CFW_CB_MSG_NOTIFY_ONLY)
uint32_t open_cfw_cb_msg_notify(uint32_t event, uint32_t value)
{
    OPEN_CFW_CALLBACK_NOTIFY(OPEN_CFW_CB_MSG_LIST, event, &value);
    return value;
}
#endif
