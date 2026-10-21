/* Native HCI driver children: ring commit 0x530084, WsfSetEvent 0x52b91e,
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
static uint32_t get32(const uint8_t *p) {uint32_t x;__builtin_memcpy(&x,p,4u);return x;}
static void put32(uint8_t *p,uint32_t x) {__builtin_memcpy(p,&x,4u);}

uint64_t audio_ble_hci_ring_commit_530084(void *ring,const void *input,uint32_t count) {
    uint8_t *r=(uint8_t *)ring;
    uint32_t bytes=get32(r+0x10u)*count;
    uint32_t saved=g2_power_critical_save();
    uint32_t accepted=0u;
    if(get32(r+0x0cu)-get32(r+8u)>=bytes) {
        const uint8_t *src=(const uint8_t *)input;
        for(uint32_t i=0u;i<bytes;i++) {
            if(src!=0) {
                uint8_t *base=(uint8_t *)(uintptr_t)get32(r+0x14u);
                base[get32(r)]=src[i];
            }
            uint32_t next=get32(r)+1u;
            put32(r,next-get32(r+0x0cu)*(next/get32(r+0x0cu)));
        }
        put32(r+8u,get32(r+8u)+bytes);
        accepted=1u;
    }
    g2_power_critical_restore(saved);
    return ((uint64_t)saved<<32)|accepted;
}

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
