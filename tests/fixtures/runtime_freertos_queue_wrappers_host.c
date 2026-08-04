/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle for the production FreeRTOS queue-wrapper source boundary.
 */

#include <string.h>

static void open_cfw_test_queue_wrapper_assert(int condition);

#define OPEN_CFW_FREERTOS_QUEUE_WRAPPER_ASSERT(condition) \
    open_cfw_test_queue_wrapper_assert((condition))

#include "../../components/apollo_main/core_overlay/runtime_freertos_queue_wrappers.c"

static struct open_cfw_queue_wrapper_control
    open_cfw_test_queue_wrapper_static_queue;
static struct open_cfw_queue_wrapper_control
    open_cfw_test_queue_wrapper_dynamic_queue;

unsigned int open_cfw_test_queue_wrapper_static_create_calls;
unsigned int open_cfw_test_queue_wrapper_dynamic_create_calls;
unsigned int open_cfw_test_queue_wrapper_initialise_mutex_calls;
unsigned int open_cfw_test_queue_wrapper_assert_calls;
unsigned int open_cfw_test_queue_wrapper_length;
unsigned int open_cfw_test_queue_wrapper_item_size;
unsigned int open_cfw_test_queue_wrapper_queue_type;
unsigned long open_cfw_test_queue_wrapper_storage;
unsigned long open_cfw_test_queue_wrapper_static_buffer;
unsigned long open_cfw_test_queue_wrapper_mutex_argument;
unsigned int open_cfw_test_queue_wrapper_static_succeeds;
unsigned int open_cfw_test_queue_wrapper_dynamic_succeeds;

static void open_cfw_test_queue_wrapper_assert(int condition)
{
    if (condition == 0)
    {
        open_cfw_test_queue_wrapper_assert_calls++;
    }
}

open_cfw_queue_wrapper_control *
open_cfw_freertos_queue_generic_create_static(
    open_cfw_queue_wrapper_ubase_type length,
    open_cfw_queue_wrapper_ubase_type item_size,
    unsigned char *storage,
    open_cfw_queue_wrapper_control *static_queue,
    open_cfw_queue_wrapper_uint8 queue_type)
{
    open_cfw_test_queue_wrapper_static_create_calls++;
    open_cfw_test_queue_wrapper_length = length;
    open_cfw_test_queue_wrapper_item_size = item_size;
    open_cfw_test_queue_wrapper_storage = (unsigned long)storage;
    open_cfw_test_queue_wrapper_static_buffer =
        (unsigned long)static_queue;
    open_cfw_test_queue_wrapper_queue_type = queue_type;

    if (open_cfw_test_queue_wrapper_static_succeeds == 0U)
    {
        return (open_cfw_queue_wrapper_control *)0;
    }
    return static_queue;
}

open_cfw_queue_wrapper_control *
open_cfw_freertos_queue_generic_create(
    open_cfw_queue_wrapper_ubase_type length,
    open_cfw_queue_wrapper_ubase_type item_size,
    open_cfw_queue_wrapper_uint8 queue_type)
{
    open_cfw_test_queue_wrapper_dynamic_create_calls++;
    open_cfw_test_queue_wrapper_length = length;
    open_cfw_test_queue_wrapper_item_size = item_size;
    open_cfw_test_queue_wrapper_storage = 0U;
    open_cfw_test_queue_wrapper_static_buffer = 0U;
    open_cfw_test_queue_wrapper_queue_type = queue_type;

    if (open_cfw_test_queue_wrapper_dynamic_succeeds == 0U)
    {
        return (struct open_cfw_queue_wrapper_control *)0;
    }
    return &open_cfw_test_queue_wrapper_dynamic_queue;
}

void open_cfw_freertos_queue_initialise_mutex(
    open_cfw_queue_wrapper_control *queue)
{
    open_cfw_test_queue_wrapper_initialise_mutex_calls++;
    open_cfw_test_queue_wrapper_mutex_argument = (unsigned long)queue;
}

void open_cfw_test_queue_wrapper_reset(void)
{
    memset(
        &open_cfw_test_queue_wrapper_static_queue,
        0xA5,
        sizeof(open_cfw_test_queue_wrapper_static_queue));
    memset(
        &open_cfw_test_queue_wrapper_dynamic_queue,
        0xA5,
        sizeof(open_cfw_test_queue_wrapper_dynamic_queue));
    open_cfw_test_queue_wrapper_static_create_calls = 0U;
    open_cfw_test_queue_wrapper_dynamic_create_calls = 0U;
    open_cfw_test_queue_wrapper_initialise_mutex_calls = 0U;
    open_cfw_test_queue_wrapper_assert_calls = 0U;
    open_cfw_test_queue_wrapper_length = 0U;
    open_cfw_test_queue_wrapper_item_size = 0U;
    open_cfw_test_queue_wrapper_queue_type = 0U;
    open_cfw_test_queue_wrapper_storage = 1U;
    open_cfw_test_queue_wrapper_static_buffer = 0U;
    open_cfw_test_queue_wrapper_mutex_argument = 0U;
    open_cfw_test_queue_wrapper_static_succeeds = 1U;
    open_cfw_test_queue_wrapper_dynamic_succeeds = 1U;
}

void *open_cfw_test_queue_wrapper_static_pointer(void)
{
    return &open_cfw_test_queue_wrapper_static_queue;
}

void *open_cfw_test_queue_wrapper_dynamic_pointer(void)
{
    return &open_cfw_test_queue_wrapper_dynamic_queue;
}

unsigned int open_cfw_test_queue_wrapper_messages(void *queue)
{
    return (
        (struct open_cfw_queue_wrapper_control *)queue
    )->messages_waiting;
}
