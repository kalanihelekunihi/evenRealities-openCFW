/* Authenticated Apollo Main HCI event masks; experimental layout. */
#include <stdint.h>

/* Stock 0x78d6dc: eight-byte HCI command mask. */
const uint8_t audio_ble_hci_event_mask_78d6dc[8] = {0x90, 0x88, 0x00, 0x02, 0x00, 0x80, 0x00, 0x20};
_Static_assert(sizeof(audio_ble_hci_event_mask_78d6dc) == 8u, "mask size");

/* Stock 0x78d6e4: eight-byte HCI command mask. */
const uint8_t audio_ble_hci_le_event_mask_78d6e4[8] = {0xff, 0xff, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00};
_Static_assert(sizeof(audio_ble_hci_le_event_mask_78d6e4) == 8u, "mask size");

/* Stock 0x78d6ec: eight-byte HCI command mask. */
const uint8_t audio_ble_hci_event_mask_page2_78d6ec[8] = {0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00};
_Static_assert(sizeof(audio_ble_hci_event_mask_page2_78d6ec) == 8u, "mask size");
