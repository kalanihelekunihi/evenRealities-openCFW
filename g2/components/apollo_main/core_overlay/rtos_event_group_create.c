/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS static/dynamic event-group creation matched to stock entries
 * 0x0047EB94 and 0x0047EBD8.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_event_group_create_uintptr;

typedef void (*open_cfw_rtos_event_group_create_void_function)(void);
typedef void (*open_cfw_rtos_event_group_create_list_function)(void *list);
typedef void *(*open_cfw_rtos_event_group_create_allocate_function)(
    unsigned int size
);

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_LIST_INITIALIZE
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_LIST_INITIALIZE(list) \
    (((open_cfw_rtos_event_group_create_list_function) \
        (open_cfw_rtos_event_group_create_uintptr)0x0045607DU)((list)))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_ALLOCATE
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_ALLOCATE(size) \
    (((open_cfw_rtos_event_group_create_allocate_function) \
        (open_cfw_rtos_event_group_create_uintptr)0x00456111U)((size)))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_OBJECT_SIZE
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_OBJECT_SIZE() 0x20U
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_BITS(group, value) \
    (*(volatile unsigned int *)(group) = (value))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_STATIC
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_STATIC(group, value) \
    (*(volatile unsigned char *)( \
        (volatile unsigned char *)(group) + 0x1CU) = (value))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_FAIL_STOP
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_event_group_create_void_function) \
            (open_cfw_rtos_event_group_create_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_event_group_create_uintptr) \
            (~(open_cfw_rtos_event_group_create_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

static __attribute__((always_inline)) inline void
open_cfw_rtos_event_group_initialize(void *group, unsigned char is_static)
{
    OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_BITS(group, 0U);
    OPEN_CFW_RTOS_EVENT_GROUP_CREATE_LIST_INITIALIZE(
        (void *)((unsigned char *)group + 0x04U)
    );
    OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_STATIC(group, is_static);
}

__attribute__((used, noinline))
void *open_cfw_rtos_event_group_static_create(void *buffer)
{
    volatile unsigned int object_size;

    if (buffer == (void *)0) {
        OPEN_CFW_RTOS_EVENT_GROUP_CREATE_FAIL_STOP();
        return (void *)0;
    }

    object_size = OPEN_CFW_RTOS_EVENT_GROUP_CREATE_OBJECT_SIZE();
    if (object_size != 0x20U) {
        OPEN_CFW_RTOS_EVENT_GROUP_CREATE_FAIL_STOP();
        return (void *)0;
    }

    open_cfw_rtos_event_group_initialize(buffer, 1U);
    return buffer;
}

__attribute__((used, noinline))
void *open_cfw_rtos_event_group_dynamic_create(void)
{
    void *group = OPEN_CFW_RTOS_EVENT_GROUP_CREATE_ALLOCATE(0x20U);

    if (group != (void *)0) {
        open_cfw_rtos_event_group_initialize(group, 0U);
    }
    return group;
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_FAIL_STOP
#undef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_STATIC
#undef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_OBJECT_SIZE
#undef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_ALLOCATE
#undef OPEN_CFW_RTOS_EVENT_GROUP_CREATE_LIST_INITIALIZE
