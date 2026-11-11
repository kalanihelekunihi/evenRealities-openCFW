#ifndef R1_NATIVE_BLE_IDENTITY_H
#define R1_NATIVE_BLE_IDENTITY_H
#include <stdint.h>
/* Separate narrow owners within native controller storage, base 0x200064b0.
 * Address records include their leading flags byte. */
extern volatile uint8_t r1_connection_parameter_profile; /* 0x200064c0 */
extern volatile uint8_t r1_ble_controller_address[7];     /* 0x200064c1 */
extern volatile uint8_t r1_ble_phone_peer_address[7];     /* 0x200064c8 */
extern volatile uint8_t r1_ble_glasses_peer_address[7];   /* 0x200064cf */
extern char r1_ble_device_name[32];                      /* 0x200064d6 */
#endif
