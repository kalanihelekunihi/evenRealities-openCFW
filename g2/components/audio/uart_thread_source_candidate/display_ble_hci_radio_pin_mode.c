/* Apollo Main ROM word 0x78ee48 is 3; literal at 0x52e93c points to it.
 * The radio pin setup at 0x52dd7c reads this mode for pin 0x8a. Native
 * ROM placement and physical pin effects remain image/hardware gates. */
#include <stdint.h>

const volatile uint32_t audio_ble_hci_radio_pin_mode = 3u;
