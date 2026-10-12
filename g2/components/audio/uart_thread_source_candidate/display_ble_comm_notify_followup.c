/* Native 0x4722cc delayed callback: send ring event 0x20, return zero. */
#include <stdint.h>
extern uint32_t Thread_SendEvtToRingTask(uint32_t flags); /* selected 0x4c543e */
uint32_t audio_ble_comm_notify_followup(void)
{
    (void)Thread_SendEvtToRingTask(0x20u);
    return 0u;
}
