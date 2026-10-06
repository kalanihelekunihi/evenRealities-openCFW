/* SPDX-License-Identifier: MIT
 * Readable source candidate for the locked Apollo bootloader queue wrappers.
 * Kernel operations below resolve to injected test providers in the
 * comparison fixture and to the recovered local provider ABI in the module
 * linker script. Their implementation/revision/configuration is not asserted.
 */
#include "queue_wrappers.h"

#define OPENCFW_QUEUE_CONTROL_BLOCK_MIN 0x50u
#define OPENCFW_SCB_ICSR               0xE000ED04u
#define OPENCFW_PENDSVSET              0x10000000u

/* Linked provider ABI: these names are aliases, not imported version claims. */
extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern opencfw_queue_handle_t opencfw_bl_kernel_queue_create_dynamic(
    uint32_t msg_count, uint32_t msg_size, uint32_t queue_type);
extern opencfw_queue_handle_t opencfw_bl_kernel_queue_create_static(
    uint32_t msg_count, uint32_t msg_size, void *mq_mem, void *cb_mem,
    uint32_t queue_type);
extern uint32_t opencfw_bl_kernel_queue_put_blocking(
    opencfw_queue_handle_t queue, const void *msg, uint32_t timeout,
    uint32_t msg_priority);
extern uint32_t opencfw_bl_kernel_queue_put_from_isr(
    opencfw_queue_handle_t queue, const void *msg, uint32_t *woken,
    uint32_t msg_priority);
extern uint32_t opencfw_bl_kernel_queue_get_blocking(
    opencfw_queue_handle_t queue, void *msg, uint32_t timeout);
extern uint32_t opencfw_bl_kernel_queue_get_from_isr(
    opencfw_queue_handle_t queue, void *msg, uint32_t *woken);

static uint32_t read_ipsr(void)
{
    uint32_t value;
    __asm__ volatile("mrs %0, ipsr" : "=r"(value));
    return value;
}

static uint32_t read_primask(void)
{
    uint32_t value;
    __asm__ volatile("mrs %0, primask" : "=r"(value));
    return value;
}

static uint32_t read_basepri(void)
{
    uint32_t value;
    __asm__ volatile("mrs %0, basepri" : "=r"(value));
    return value;
}

/* 0x41602A. The runtime-mode helper returns 1/2/0 from two state words. */
__attribute__((noinline))
uint32_t opencfw_bl_queue_is_nonblocking_context(void)
{
    if (read_ipsr() != 0u)
        return 1u;
    /* Stock branches straight to return-0 when the helper reports state 1. */
    if (opencfw_bl_queue_runtime_mode() == 1u)
        return 0u;
    if (read_primask() != 0u)
        return 1u;
    /* Keep the zero/nonzero result explicit in ordinary M-class opcodes;
     * the stock source decision is simply BASEPRI != 0. */
    volatile uint32_t basepri_active = 0u;
    if (read_basepri() != 0u)
        basepri_active = 1u;
    return basepri_active;
}

/* 0x416816. Product intentionally wraps modulo 2^32, as original MUL.W does. */
opencfw_queue_handle_t opencfw_bl_queue_create(
    uint32_t msg_count, uint32_t msg_size, const opencfw_queue_attr_t *attr)
{
    if (opencfw_bl_queue_is_nonblocking_context() != 0u ||
        msg_count == 0u || msg_size == 0u)
        return (opencfw_queue_handle_t)0;

    if (attr == 0)
        return opencfw_bl_kernel_queue_create_dynamic(msg_count, msg_size, 0u);

    const uint32_t required = msg_count * msg_size;
    const uint32_t has_static_storage =
        attr->cb_mem != 0 && attr->cb_size >= OPENCFW_QUEUE_CONTROL_BLOCK_MIN &&
        attr->mq_mem != 0 && attr->mq_size >= required;
    const uint32_t requests_dynamic_storage =
        attr->cb_mem == 0 && attr->cb_size == 0u &&
        attr->mq_mem == 0 && attr->mq_size == 0u;

    if (has_static_storage)
        return opencfw_bl_kernel_queue_create_static(
            msg_count, msg_size, attr->mq_mem, attr->cb_mem, 0u);
    if (requests_dynamic_storage)
        return opencfw_bl_kernel_queue_create_dynamic(msg_count, msg_size, 0u);
    return (opencfw_queue_handle_t)0;
}

static void pend_deferred_switch(uint32_t woken)
{
    if (woken != 0u)
        *(volatile uint32_t *)(uintptr_t)OPENCFW_SCB_ICSR = OPENCFW_PENDSVSET;
}

static __attribute__((noinline)) int32_t queue_failure(uint32_t timeout)
{
    volatile int32_t status = OPENCFW_OS_ERROR_RESOURCE;
    if (timeout != 0u)
        status = OPENCFW_OS_ERROR_TIMEOUT;
    return status;
}

/* 0x4168A2; msg_priority is accepted by the public ABI but ignored. */
int32_t opencfw_bl_queue_put(opencfw_queue_handle_t queue, const void *msg,
                              uint32_t msg_priority, uint32_t timeout)
{
    (void)msg_priority;
    if (opencfw_bl_queue_is_nonblocking_context() == 0u) {
        if (queue == 0)
            return OPENCFW_OS_ERROR_PARAMETER;
        if (msg == 0)
            return OPENCFW_OS_ERROR_PARAMETER;
        if (opencfw_bl_kernel_queue_put_blocking(queue, msg, timeout, 0u) == 1u)
            return OPENCFW_OS_OK;
        return queue_failure(timeout);
    }

    if (queue == 0)
        return OPENCFW_OS_ERROR_PARAMETER;
    if (msg == 0)
        return OPENCFW_OS_ERROR_PARAMETER;
    if (timeout != 0u)
        return OPENCFW_OS_ERROR_PARAMETER;
    uint32_t woken = 0u;
    if (opencfw_bl_kernel_queue_put_from_isr(queue, msg, &woken, 0u) != 1u)
        return OPENCFW_OS_ERROR_RESOURCE;
    pend_deferred_switch(woken);
    return OPENCFW_OS_OK;
}

/* 0x416920; output msg_priority is not touched by the original instructions. */
int32_t opencfw_bl_queue_get(opencfw_queue_handle_t queue, void *msg,
                              uint32_t *msg_priority, uint32_t timeout)
{
    (void)msg_priority;
    if (opencfw_bl_queue_is_nonblocking_context() == 0u) {
        if (queue == 0)
            return OPENCFW_OS_ERROR_PARAMETER;
        if (msg == 0)
            return OPENCFW_OS_ERROR_PARAMETER;
        if (opencfw_bl_kernel_queue_get_blocking(queue, msg, timeout) == 1u)
            return OPENCFW_OS_OK;
        return queue_failure(timeout);
    }

    if (queue == 0)
        return OPENCFW_OS_ERROR_PARAMETER;
    if (msg == 0)
        return OPENCFW_OS_ERROR_PARAMETER;
    if (timeout != 0u)
        return OPENCFW_OS_ERROR_PARAMETER;
    uint32_t woken = 0u;
    if (opencfw_bl_kernel_queue_get_from_isr(queue, msg, &woken) != 1u)
        return OPENCFW_OS_ERROR_RESOURCE;
    pend_deferred_switch(woken);
    return OPENCFW_OS_OK;
}
