#include <stdint.h>
static volatile uint32_t *const mpu_control=(volatile uint32_t *)(uintptr_t)0xe000ed94u;
static volatile uint32_t *const system_handler_control=(volatile uint32_t *)(uintptr_t)0xe000ed24u;
void audio_uart_mpu_enable_registers_4d43b4(uint32_t flags) {
    __asm__ volatile("dmb sy" ::: "memory");
    *mpu_control=flags|1u;
    *system_handler_control|=0x10000u;
    __asm__ volatile("dsb sy" ::: "memory");
    __asm__ volatile("isb sy" ::: "memory");
}
void audio_uart_mpu_disable_registers_4d43d4(void) {
    __asm__ volatile("dmb sy" ::: "memory");
    *system_handler_control&=~0x10000u;
    *mpu_control&=~1u;
    __asm__ volatile("dsb sy" ::: "memory");
    __asm__ volatile("isb sy" ::: "memory");
}
uint32_t audio_uart_mpu_reset_4d44e2(void) {
    audio_uart_mpu_disable_registers_4d43d4();
    return 0u;
}
uint32_t audio_uart_mpu_enable_4d44ec(uint32_t privileged_default,uint32_t fault_enable) {
    uint32_t flags=((uint32_t)(uint8_t)privileged_default<<2)|((uint32_t)(uint8_t)fault_enable<<1);
    if((*mpu_control&1u)!=0u)return 3u;
    audio_uart_mpu_enable_registers_4d43b4(flags);
    return 0u;
}
