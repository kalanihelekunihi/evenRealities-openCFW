/* Both names refer to native 0x4bc418, already source-defined and bounded
 * by audio_ble_master_success_delayed. Preserve the same argument/return ABI. */
#include <stdint.h>
extern uint32_t audio_ble_master_success_delayed(uint32_t notification);
__attribute__((naked)) uint32_t audio_ble_comm_notify_ring_delayed(uint32_t notification __attribute__((unused)))
{
    __asm volatile("b audio_ble_master_success_delayed");
}
__attribute__((naked)) uint32_t PB_TxEncodeNotifyRingConnectInfo(uint32_t notification __attribute__((unused)))
{
    __asm volatile("b audio_ble_master_success_delayed");
}
