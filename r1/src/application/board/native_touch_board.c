/* Native ready-line active byte 200067f8. Adjacent input/callback words
 * share the paired owner in native_peripheral_bindings.c. */
#include "native_touch_board.h"
#include "../registry/stock_registry.h"
volatile uint8_t r1_touch_board_active
    __attribute__((section(".r1.touch.board.active"),aligned(4)));
extern void r1_touch_bus_acquire_on(void), r1_touch_bus_enable_on(void);
extern uint32_t r1_touch_device_op_stop(void),r1_touch_device_op_lock1(void);
extern uint32_t r1_touch_device_op_unlock(void),r1_touch_record_op_0c(void);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_touch_task_event_post(uint32_t);
uint32_t r1_touch_ready_callback_setter(uint32_t callback)
{
    if (callback == 0)
        return 0;
    r1_touch_ready_callback_word = callback;
    return 1;
}
uint32_t r1_touch_ready_irq_callback(void)
{
    return r1_touch_task_event_post(1);
}
uint32_t r1_touch_board_open(void)
{
    uint32_t active = r1_touch_board_active;
    if (active != 0)
        return active;
    r1_touch_bus_acquire_on();
    (void)osDelay(10);
    (void)r1_touch_device_op_stop();
    (void)r1_touch_device_op_lock1();
    (void)r1_touch_device_op_unlock();
    (void)osDelay(130);
    (void)r1_touch_device_op_lock1();
    (void)osDelay(10);
    (void)r1_touch_record_op_0c();
    (void)osDelay(20);
    (void)r1_stock_dispatch_08(r1_touch_input_device);
    uint64_t snapshot = r1_touch_ready_storage.words;
    generic_device_registry_device *input = (void *)(uintptr_t)(uint32_t)snapshot;
    uintptr_t callback = (uint32_t)(snapshot >> 32);
    (void)r1_stock_dispatch_20(input, 1, callback);
    (void)osDelay(20);
    r1_touch_board_active = 1;
    return 1;
}
/* Historical label: actual stock operation is LDO release then output low. */
uint32_t r1_touch_power_on_step(void)
{
    r1_touch_bus_enable_on();
    __attribute__((musttail)) return r1_touch_device_op_unlock();
}
uintptr_t r1_touch_pending_flag_consume(void)
{
    if (r1_touch_board_active == 0)
        return (uintptr_t)&r1_touch_board_active;
    r1_touch_board_active = 0;
    (void)r1_touch_device_op_stop();
    __attribute__((musttail)) return r1_touch_power_on_step();
}
