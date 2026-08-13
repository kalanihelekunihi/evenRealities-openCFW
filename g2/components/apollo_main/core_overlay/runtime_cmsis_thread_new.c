/* Copyright (c) 2013-2022 Arm Limited. SPDX-License-Identifier: Apache-2.0 */
typedef __UINT32_TYPE__ open_cfw_cmsis_thread_new_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_thread_new_int32;
typedef __UINT16_TYPE__ open_cfw_cmsis_thread_new_stack_depth;

typedef void (*open_cfw_cmsis_thread_new_function)(void *argument);

struct open_cfw_cmsis_thread_new_attributes {
    const char *name;
    open_cfw_cmsis_thread_new_uint32 attribute_bits;
    void *control_block_memory;
    open_cfw_cmsis_thread_new_uint32 control_block_size;
    void *stack_memory;
    open_cfw_cmsis_thread_new_uint32 stack_size;
    open_cfw_cmsis_thread_new_int32 priority;
    open_cfw_cmsis_thread_new_uint32 trustzone_module;
    open_cfw_cmsis_thread_new_uint32 reserved;
};

extern open_cfw_cmsis_thread_new_uint32 open_cfw_cmsis_irq_context(void);
extern void *open_cfw_retained_freertos_task_create_static(
    open_cfw_cmsis_thread_new_function function,
    const char *name,
    open_cfw_cmsis_thread_new_uint32 stack_depth,
    void *argument,
    open_cfw_cmsis_thread_new_uint32 priority,
    void *stack_memory,
    void *control_block_memory
);
extern open_cfw_cmsis_thread_new_int32 open_cfw_retained_freertos_task_create(
    open_cfw_cmsis_thread_new_function function,
    const char *name,
    open_cfw_cmsis_thread_new_stack_depth stack_depth,
    void *argument,
    open_cfw_cmsis_thread_new_uint32 priority,
    void **created_task
);

__attribute__((used,noinline))
void *open_cfw_cmsis_thread_new(
    open_cfw_cmsis_thread_new_function function,
    void *argument,
    const struct open_cfw_cmsis_thread_new_attributes *attributes
)
{
    const char *name = (void *)0;
    open_cfw_cmsis_thread_new_uint32 stack_depth = 1024U;
    open_cfw_cmsis_thread_new_uint32 priority = 24U;
    open_cfw_cmsis_thread_new_int32 memory_kind = -1;
    void *task = (void *)0;

    if ((open_cfw_cmsis_irq_context() != 0U) || (function == (void *)0)) {
        return (void *)0;
    }

    if (attributes == (void *)0) {
        memory_kind = 0;
    } else {
        if (attributes->name != (void *)0) name = attributes->name;
        if (attributes->priority != 0) {
            priority = (open_cfw_cmsis_thread_new_uint32)attributes->priority;
        }
        if ((priority < 1U) || (priority > 56U) ||
            ((attributes->attribute_bits & 1U) != 0U)) {
            return (void *)0;
        }
        if (attributes->stack_size > 0U) {
            stack_depth = attributes->stack_size / 4U;
        }
        if ((attributes->control_block_memory != (void *)0) &&
            (attributes->control_block_size >= 112U) &&
            (attributes->stack_memory != (void *)0) &&
            (attributes->stack_size > 0U)) {
            memory_kind = 1;
        } else if ((attributes->control_block_memory == (void *)0) &&
                   (attributes->control_block_size == 0U) &&
                   (attributes->stack_memory == (void *)0)) {
            memory_kind = 0;
        }
    }

    if (memory_kind == 1) {
        task = open_cfw_retained_freertos_task_create_static(
            function, name, stack_depth, argument, priority,
            attributes->stack_memory, attributes->control_block_memory
        );
    } else if (memory_kind == 0) {
        if (open_cfw_retained_freertos_task_create(
                function, name,
                (open_cfw_cmsis_thread_new_stack_depth)stack_depth,
                argument, priority, &task) != 1) {
            task = (void *)0;
        }
    }
    return task;
}
