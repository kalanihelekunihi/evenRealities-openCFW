/* Copyright (c) 2013-2022 Arm Limited. SPDX-License-Identifier: Apache-2.0 */
typedef __UINT32_TYPE__ open_cfw_cmsis_thread_flags_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_thread_flags_int32;
struct open_cfw_freertos_notify_tcb;
extern open_cfw_cmsis_thread_flags_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_thread_flags_uint32 open_cfw_freertos_task_get_tick_count(void);
extern open_cfw_cmsis_thread_flags_int32 open_cfw_freertos_task_notify(
    struct open_cfw_freertos_notify_tcb *, open_cfw_cmsis_thread_flags_uint32,
    open_cfw_cmsis_thread_flags_uint32, int,
    open_cfw_cmsis_thread_flags_uint32 *
);
extern open_cfw_cmsis_thread_flags_int32 open_cfw_freertos_task_notify_from_isr(
    struct open_cfw_freertos_notify_tcb *, open_cfw_cmsis_thread_flags_uint32,
    open_cfw_cmsis_thread_flags_uint32, int,
    open_cfw_cmsis_thread_flags_uint32 *, open_cfw_cmsis_thread_flags_int32 *
);
extern open_cfw_cmsis_thread_flags_int32 open_cfw_freertos_task_notify_wait(
    open_cfw_cmsis_thread_flags_uint32, open_cfw_cmsis_thread_flags_uint32,
    open_cfw_cmsis_thread_flags_uint32,
    open_cfw_cmsis_thread_flags_uint32 *, open_cfw_cmsis_thread_flags_uint32
);

#ifndef OPEN_CFW_CMSIS_THREAD_FLAGS_PENDSV
#define OPEN_CFW_CMSIS_THREAD_FLAGS_PENDSV() \
    (*(volatile open_cfw_cmsis_thread_flags_uint32 *)0xE000ED04U = 0x10000000U)
#endif

#if !defined(OPEN_CFW_BUILD_CMSIS_THREAD_FLAGS_SET) && \
    !defined(OPEN_CFW_BUILD_CMSIS_THREAD_FLAGS_WAIT)
#define OPEN_CFW_BUILD_CMSIS_THREAD_FLAGS_ALL 1
#endif

#if defined(OPEN_CFW_BUILD_CMSIS_THREAD_FLAGS_ALL) || \
    defined(OPEN_CFW_BUILD_CMSIS_THREAD_FLAGS_SET)
__attribute__((used,noinline))
open_cfw_cmsis_thread_flags_uint32 open_cfw_cmsis_thread_flags_set(
    struct open_cfw_freertos_notify_tcb *task,
    open_cfw_cmsis_thread_flags_uint32 flags
)
{
    open_cfw_cmsis_thread_flags_uint32 result = 0xFFFFFFFFU;
    open_cfw_cmsis_thread_flags_int32 yield_required = 0;
    if ((task == (void *)0) || ((flags & 0x80000000U) != 0U)) return 0xFFFFFFFCU;
    if (open_cfw_cmsis_irq_context() != 0U) {
        (void)open_cfw_freertos_task_notify_from_isr(task,0U,flags,1,0,&yield_required);
        (void)open_cfw_freertos_task_notify_from_isr(task,0U,0U,0,&result,0);
        if (yield_required != 0) OPEN_CFW_CMSIS_THREAD_FLAGS_PENDSV();
    } else {
        (void)open_cfw_freertos_task_notify(task,0U,flags,1,0);
        (void)open_cfw_freertos_task_notify(task,0U,0U,0,&result);
    }
    return result;
}
#endif

#if defined(OPEN_CFW_BUILD_CMSIS_THREAD_FLAGS_ALL) || \
    defined(OPEN_CFW_BUILD_CMSIS_THREAD_FLAGS_WAIT)
__attribute__((used,noinline))
open_cfw_cmsis_thread_flags_uint32 open_cfw_cmsis_thread_flags_wait(
    open_cfw_cmsis_thread_flags_uint32 flags,
    open_cfw_cmsis_thread_flags_uint32 options,
    open_cfw_cmsis_thread_flags_uint32 timeout
)
{
    open_cfw_cmsis_thread_flags_uint32 result, value, clear, start, delta, wait;
    open_cfw_cmsis_thread_flags_int32 passed;
    if (open_cfw_cmsis_irq_context() != 0U) return 0xFFFFFFFAU;
    if ((flags & 0x80000000U) != 0U) return 0xFFFFFFFCU;
    clear = ((options & 2U) != 0U) ? 0U : flags;
    result = 0U; wait = timeout; start = open_cfw_freertos_task_get_tick_count();
    do {
        passed = open_cfw_freertos_task_notify_wait(0U,0U,clear,&value,wait);
        if (passed != 0) {
            result &= flags;
            result |= value;
            if ((options & 1U) != 0U) {
                if ((flags & result) == flags) break;
            } else if ((flags & result) != 0U) {
                break;
            }
            if (timeout == 0U) { result = 0xFFFFFFFDU; break; }
            delta = open_cfw_freertos_task_get_tick_count() - start;
            wait = (delta > timeout) ? 0U : timeout - delta;
        } else {
            result = (timeout == 0U) ? 0xFFFFFFFDU : 0xFFFFFFFEU;
        }
    } while (passed != 0);
    return result;
}
#endif
