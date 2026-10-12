#include <stdint.h>
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
void g2_tlsf_control_construct_4d0524(void *cell) {
    volatile uint32_t *words=cell;
    words[2]=(uint32_t)(uintptr_t)cell;words[3]=(uint32_t)(uintptr_t)cell;words[4]=0;
    for(uint32_t fl=0;fl<24u;fl++) {
        words[5u+fl]=0;
        for(uint32_t sl=0;sl<32u;sl++) words[29u+fl*32u+sl]=(uint32_t)(uintptr_t)cell;
    }
}
void *g2_tlsf_control_create_4d06b4(void *memory) {
    if(((uintptr_t)memory&3u)!=0u) {
        audio_ble_hci_boot_log_4733ee((const char *)(uintptr_t)0x72f49cu,4u);
        return 0;
    }
    g2_tlsf_control_construct_4d0524(memory);
    return memory;
}
