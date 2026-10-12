#include <stdint.h>
extern uint32_t audio_uart_mpu_reset_4d44e2(void);
extern uint32_t audio_uart_mpu_attributes_4d450c(const void *,uint32_t);
extern uint32_t audio_uart_mpu_region_4d4596(const void *,uint32_t);
extern uint32_t audio_uart_mpu_enable_4d44ec(uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t);
/* Authenticated non-executable descriptor words at789fec/774bc4/774bdc. */
static const uint32_t secondary[6]={6u,0x2013be70u,0x10100u,0x20208e6fu,0u,1u};
static const uint32_t small[6]={7u,0x20378d9cu,0x10100u,0x2037919bu,0u,1u};
void audio_uart_heap_memory_configure_4840c8(void) {
    uint32_t attributes[3];
    uint32_t secondary_copy[6],small_copy[6];
    (void)audio_uart_mpu_reset_4d44e2();
    attributes[0]=0x1000100u;attributes[1]=0x1000000u;attributes[2]=0u;
    (void)audio_uart_mpu_attributes_4d450c(attributes,1u);
    audio_uart_checksum_copy(secondary_copy,secondary,24u);
    (void)audio_uart_mpu_region_4d4596(secondary_copy,1u);
    audio_uart_checksum_copy(small_copy,small,24u);
    (void)audio_uart_mpu_region_4d4596(small_copy,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x200007bcu,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x200007d4u,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x20000630u,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x20000c20u,1u);
    audio_ble_privacy_cache_maintenance(0,1u);
    (void)audio_uart_mpu_enable_4d44ec(1u,1u);
}
