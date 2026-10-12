#include <stdint.h>
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
extern void g2_tlsf_block_set_size(void *,uint32_t);
extern void g2_tlsf_block_insert(void *,void *);
extern void *g2_tlsf_block_link_next(void *);
extern void g2_tlsf_block_set_prev_free(void *);
static uint32_t config(uint32_t address) {return *(const volatile uint32_t *)(uintptr_t)address;}
void g2_tlsf_block_set_free_4cfdc0(void *block) {
    uint32_t mask=config(0x78f4b4u);
    *(volatile uint32_t *)((uint8_t *)block+4u)|=mask;
}
void g2_tlsf_block_set_used_4cfdce(void *block) {
    uint32_t mask=config(0x78f4b4u);
    *(volatile uint32_t *)((uint8_t *)block+4u)&=~mask;
}
extern void g2_tlsf_block_clear_prev_free(void *);
void *g2_tlsf_add_pool_4d0608(void *control,void *memory,uint32_t bytes) {
    uint32_t overhead=config(0x78f4bcu)*2u;
    uint32_t size=(bytes-overhead)&~3u;
    if(((uintptr_t)memory&3u)!=0u) {
        audio_ble_hci_boot_log_4733ee((const char *)(uintptr_t)0x72f468u,4u);
        return 0;
    }
    if(size<config(0x78f4c4u)||config(0x78f4c8u)<size) {
        uint32_t max=config(0x78f4c8u)+overhead;
        uint32_t min=config(0x78f4c4u)+overhead;
        audio_ble_hci_boot_log_4733ee((const char *)(uintptr_t)0x710764u,min,max);
        return 0;
    }
    void *block=(void *)((uintptr_t)memory-config(0x78f4bcu));
    g2_tlsf_block_set_size(block,size);
    g2_tlsf_block_set_free_4cfdc0(block);
    g2_tlsf_block_clear_prev_free(block);
    g2_tlsf_block_insert(control,block);
    void *last=g2_tlsf_block_link_next(block);
    g2_tlsf_block_set_size(last,0u);
    g2_tlsf_block_set_used_4cfdce(last);
    g2_tlsf_block_set_prev_free(last);
    return memory;
}
