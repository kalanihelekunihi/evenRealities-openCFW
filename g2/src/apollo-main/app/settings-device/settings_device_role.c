/* Native 0x45a568 is a byte getter of live cell 0x20075024, the same cell
 * already used by selected service-mode getter 0x45a570. */
#include <stdint.h>
extern volatile uint8_t g2_audio_service_mode;
uint32_t audio_settings_device_role(void) {return g2_audio_service_mode;}
