/* FreeRTOS static idle-task memory callback (configSUPPORT_STATIC_ALLOCATION).
 * Native 0x48d558..0x48d566, literal pool 0x48d568..0x48d56f.
 *
 * Stock vApplicationGetIdleTaskMemory: its only caller is vTaskStartScheduler
 * (bl at 0x454cfe), which passes the result to xTaskCreateStatic with the
 * name "IDLE" (ROM 0x78eaa4). Stack depth 0x400 words (4 KiB). */
#include <stdint.h>

extern uint8_t g2_idle_task_tcb_20071e30[];   /* RAM 0x20071e30, StaticTask_t */
extern uint32_t g2_idle_task_stack_2005f154[]; /* RAM 0x2005f154, StackType_t[0x400] */

void vApplicationGetIdleTaskMemory_48d558(void **tcb_buffer, uint32_t **stack_buffer,
                                          uint32_t *stack_size);

/* 0x48d558 */
void vApplicationGetIdleTaskMemory_48d558(void **tcb_buffer, uint32_t **stack_buffer,
                                          uint32_t *stack_size)
{
    *tcb_buffer = g2_idle_task_tcb_20071e30;
    *stack_buffer = g2_idle_task_stack_2005f154;
    *stack_size = 0x400u;
}
