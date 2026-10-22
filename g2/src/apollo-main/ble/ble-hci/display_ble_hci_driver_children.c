/* Native HCI driver children: WsfSetEvent 0x52b91e,
 * error_check 0x4b47ae, and architectural IRQ pair 0x473940/0x5300d8. */
#include <stdint.h>
extern uint8_t audio_wsf_task_state[]; /* live 0x20073230, ROM slot 0x52bac4 */
extern volatile uint32_t audio_ble_hci_error_value_20074648; /* 0x4b4d3c */
extern uint32_t audio_ble_hci_error_callback_20074644; /* 0x4b4d40 */
extern void audio_wsf_cs_enter(void);
extern void audio_wsf_cs_exit(void);
extern void audio_wsf_set_os_event(void);

__attribute__((noinline)) uint32_t g2_power_critical_save(void) {
    uint32_t primask;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(primask) :: "memory");
    return primask;
}
__attribute__((noinline)) void g2_power_critical_restore(uint32_t primask) {
    __asm__ volatile("msr primask, %0" :: "r"(primask) : "memory");
}

/* 0x530084 is am_hal_queue_item_add (AmbiqSuite 5.1.0 hal/am_hal_queue.c);
 * audio_ble_hci_ring_commit_530084 is a payload defsym alias of it. */

uint32_t audio_ble_wsf_set_event_body(uint32_t handler,uint32_t mask,
                                      uint32_t scratch,uint32_t high) {
    (void)scratch;
    audio_wsf_cs_enter();
    audio_wsf_task_state[0x28u+(handler&0xfu)]|=(uint8_t)mask;
    audio_wsf_task_state[0x3cu]|=4u;
    audio_wsf_cs_exit();
    audio_wsf_set_os_event();
    return high;
}
__attribute__((naked)) uint32_t audio_ble_wsf_set_event(uint32_t handler,uint32_t mask) {
    __asm volatile("b audio_ble_wsf_set_event_body");
}

void audio_ble_hci_error_check_body(uint32_t code) {
    if(code!=0u) {
        audio_ble_hci_error_value_20074648=code;
        uint32_t callback=audio_ble_hci_error_callback_20074644;
        if(callback!=0u)((void (*)(uint32_t))(uintptr_t)callback)(code);
    }
}
__attribute__((naked)) uint32_t audio_ble_hci_error_check_4b47ae(uint32_t code) {
    __asm volatile("push {r7, lr}\n\tbl audio_ble_hci_error_check_body\n\tpop {r7, lr}\n\tmov r0, r7\n\tbx lr");
}
