/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the G2 generic callback manager.  The stock
 * EasyLogger branches are diagnostic-only and are deliberately omitted; the
 * list ABI, allocation policy, return values, duplicate handling, ordering,
 * count maintenance, and callback dispatch behavior are preserved.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_CALLBACK_MGR_CREATE_ONLY) && \
    !defined(OPEN_CFW_CALLBACK_MGR_DELETE_ONLY) && \
    !defined(OPEN_CFW_CALLBACK_MGR_INIT_ONLY) && \
    !defined(OPEN_CFW_CALLBACK_MGR_DEINIT_ONLY) && \
    !defined(OPEN_CFW_CALLBACK_MGR_IS_REGISTERED_ONLY) && \
    !defined(OPEN_CFW_CALLBACK_MGR_REGISTER_ONLY) && \
    !defined(OPEN_CFW_CALLBACK_MGR_UNREGISTER_ONLY) && \
    !defined(OPEN_CFW_CALLBACK_MGR_NOTIFY_ONLY)
#define OPEN_CFW_CALLBACK_MGR_ALL 1
#endif

typedef struct open_cfw_callback_node {
    uintptr_t callback;
    struct open_cfw_callback_node *next;
} open_cfw_callback_node_t;

typedef struct {
    open_cfw_callback_node_t *head;
    uint8_t count;
    uint8_t reserved[3];
    const char *type;
} open_cfw_callback_manager_t;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_callback_node_t) == 8u,
    "G2 callback node ABI changed");
_Static_assert(sizeof(open_cfw_callback_manager_t) == 12u,
    "G2 callback manager ABI changed");
_Static_assert(offsetof(open_cfw_callback_manager_t, count) == 4u,
    "G2 callback count offset changed");
_Static_assert(offsetof(open_cfw_callback_manager_t, type) == 8u,
    "G2 callback type offset changed");
#endif

#ifndef OPEN_CFW_CALLBACK_MGR_ALLOC
void *open_cfw_file_heap_allocate(uint32_t size);
#define OPEN_CFW_CALLBACK_MGR_ALLOC(size) \
    open_cfw_file_heap_allocate((uint32_t)(size))
#endif

#ifndef OPEN_CFW_CALLBACK_MGR_FREE
void open_cfw_file_heap_free(void *allocation);
#define OPEN_CFW_CALLBACK_MGR_FREE(allocation) \
    open_cfw_file_heap_free((allocation))
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_CREATE_ONLY)
open_cfw_callback_node_t *open_cfw_callback_mgr_create(uintptr_t callback)
{
    open_cfw_callback_node_t *node =
        (open_cfw_callback_node_t *)OPEN_CFW_CALLBACK_MGR_ALLOC(
            sizeof(open_cfw_callback_node_t));

    if (node != NULL) {
        node->callback = callback;
        node->next = NULL;
    }
    return node;
}
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_DELETE_ONLY)
void open_cfw_callback_mgr_delete(open_cfw_callback_node_t *node)
{
    if (node != NULL) {
        OPEN_CFW_CALLBACK_MGR_FREE(node);
    }
}
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_INIT_ONLY)
uint32_t open_cfw_callback_mgr_init(open_cfw_callback_manager_t *manager,
    const char *type)
{
    if (manager == NULL) {
        return 0u;
    }
    manager->head = NULL;
    manager->count = 0u;
    manager->type = type;
    return 1u;
}
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_DEINIT_ONLY)
void open_cfw_callback_mgr_delete(open_cfw_callback_node_t *node);

void open_cfw_callback_mgr_deinit(open_cfw_callback_manager_t *manager)
{
    open_cfw_callback_node_t *node;

    if (manager == NULL) {
        return;
    }
    node = manager->head;
    while (node != NULL) {
        open_cfw_callback_node_t *next = node->next;
        open_cfw_callback_mgr_delete(node);
        node = next;
    }
    manager->head = NULL;
    manager->count = 0u;
}
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_IS_REGISTERED_ONLY)
uint32_t open_cfw_callback_mgr_is_registered(
    const open_cfw_callback_manager_t *manager, uintptr_t callback)
{
    const open_cfw_callback_node_t *node;

    if ((manager == NULL) || (callback == (uintptr_t)0u)) {
        return 0u;
    }
    node = manager->head;
    while (node != NULL) {
        if (node->callback == callback) {
            return 1u;
        }
        node = node->next;
    }
    return 0u;
}
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_REGISTER_ONLY)
uint32_t open_cfw_callback_mgr_is_registered(
    const open_cfw_callback_manager_t *manager, uintptr_t callback);
open_cfw_callback_node_t *open_cfw_callback_mgr_create(uintptr_t callback);

uint32_t open_cfw_callback_mgr_register(open_cfw_callback_manager_t *manager,
    uintptr_t callback)
{
    open_cfw_callback_node_t *node;

    if ((manager == NULL) || (callback == (uintptr_t)0u)) {
        return 0u;
    }
    if (open_cfw_callback_mgr_is_registered(manager, callback) != 0u) {
        return 1u;
    }
    node = open_cfw_callback_mgr_create(callback);
    if (node == NULL) {
        return 0u;
    }
    node->next = manager->head;
    manager->head = node;
    manager->count = (uint8_t)(manager->count + 1u);
    return 1u;
}
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_UNREGISTER_ONLY)
void open_cfw_callback_mgr_delete(open_cfw_callback_node_t *node);

void open_cfw_callback_mgr_unregister(open_cfw_callback_manager_t *manager,
    uintptr_t callback)
{
    open_cfw_callback_node_t *node;
    open_cfw_callback_node_t *previous = NULL;

    if ((manager == NULL) || (callback == (uintptr_t)0u)) {
        return;
    }
    node = manager->head;
    while (node != NULL) {
        if (node->callback == callback) {
            if (previous == NULL) {
                manager->head = node->next;
            } else {
                previous->next = node->next;
            }
            open_cfw_callback_mgr_delete(node);
            manager->count = (uint8_t)(manager->count - 1u);
            return;
        }
        previous = node;
        node = node->next;
    }
}
#endif

#if defined(OPEN_CFW_CALLBACK_MGR_ALL) || \
    defined(OPEN_CFW_CALLBACK_MGR_NOTIFY_ONLY)
typedef void (*open_cfw_callback_fn_t)(uint32_t event, uintptr_t value);

void open_cfw_callback_mgr_notify(const open_cfw_callback_manager_t *manager,
    uint32_t event, uintptr_t value)
{
    const open_cfw_callback_node_t *node;

    if ((manager == NULL) || (manager->head == NULL) ||
        (manager->count == 0u)) {
        return;
    }
    node = manager->head;
    while (node != NULL) {
        if (node->callback != (uintptr_t)0u) {
            ((open_cfw_callback_fn_t)node->callback)(event, value);
        }
        node = node->next;
    }
}
#endif
