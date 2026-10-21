/* Native 0x44ab24 system reset and its 0x44b0ae wrapper. AIRCR 0xe000ed0c
 * and VECTKEY/SYSRESETREQ 0x05fa0004 are authenticated ROM literals. */
#include <stdint.h>
#define AIRCR (*(volatile uint32_t *)(uintptr_t)0xe000ed0cu)
__attribute__((noreturn)) void audio_ble_system_reset_44ab24(void) {
    __asm__ volatile("dsb sy" ::: "memory");
    AIRCR=(AIRCR&0x700u)|0x05fa0004u;
    __asm__ volatile("dsb sy" ::: "memory");
    for(;;) { __asm__ volatile("" ::: "memory"); }
}
void audio_ble_radio_ready_44b0ae(void) {
    audio_ble_system_reset_44ab24();
}
