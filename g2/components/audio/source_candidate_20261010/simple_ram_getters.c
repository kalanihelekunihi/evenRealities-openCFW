#include <stdint.h>

/* Original entry 0x43d0ce: LDR literal 0x20004543, LDRB [r0], BX LR. */
uint32_t platform_log_flags(void) {
    return *(volatile const uint8_t *)(uintptr_t)0x20004543u;
}
uint32_t stock_audio_log_mask(void) __attribute__((alias("platform_log_flags")));
uint32_t audio_log_flags(void) __attribute__((alias("platform_log_flags")));

/* Original entry 0x4abe60: LDR literal 0x200038f0, LDRB [r0,#1], BX LR. */
uint32_t audio_role(void) {
    return *(volatile const uint8_t *)(uintptr_t)0x200038f1u;
}
