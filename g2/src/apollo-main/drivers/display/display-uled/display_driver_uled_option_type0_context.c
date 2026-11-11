/* Apollo S200 brightness context byte getter at 0x46bfe8. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_settings_config_live[] __asm__("audio_settings_config_live");

uint32_t display_driver_uled_type0_context_46bfe8(void) {
    return *(volatile const uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_settings_config_live+0x1u);
}
