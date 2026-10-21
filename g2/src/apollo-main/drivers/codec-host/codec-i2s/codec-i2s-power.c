#include <stdint.h>

/* Stock 0x00590648 is already reduced as audio_i2s_power_selected,
 * including mode 0 and the mode 1/2 power-down/backup branches. */
extern uint32_t audio_i2s_power_selected(uint32_t *handle,
                                          uint32_t mode, uint32_t backup);

uint32_t g2_codec_i2s_disable(void *handle,
                               uint32_t mode, uint32_t backup) {
    return audio_i2s_power_selected((uint32_t *)handle, mode, backup);
}
