/* Apollo Main compressed SRAM initializer record 0x75d3f4 places these
 * two LE feature words at native 0x20000028. Decoded startup bytes are
 * ff 37 00 00 00 00 00 00; HciSetLeSupFeat mutates both words later.
 * Exact runtime placement and the whole startup scatter remain open. */
#include <stdint.h>

uint32_t audio_ble_hci_le_supported_features[2u] = {0x000037ffu, 0u};
