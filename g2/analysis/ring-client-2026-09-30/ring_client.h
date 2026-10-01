/* Recovered G2 s200_v2.2.6.10 ring-client constants.
 * Evidence: README.md, disassembly.txt, validation.json beside this file.
 * Describes G2's selected service/characteristics, not all R1 services.
 * No hardware access or firmware binary is embedded here. */
#ifndef OPENCFW_RECOVERED_RING_CLIENT_H
#define OPENCFW_RECOVERED_RING_CLIENT_H
#include <stdint.h>
#define G2_RING_SERVICE_UUID "bae80001-4f05-4503-8e65-3af1f7329d1f"
#define G2_RING_WRITE_UUID   "bae80010-4f05-4503-8e65-3af1f7329d1f"
#define G2_RING_NOTIFY_UUID  "bae80011-4f05-4503-8e65-3af1f7329d1f"
#define G2_RING_CCCD_UUID16  UINT16_C(0x2902)
/* Defaults written at init AND each central connection-open, not universal
 * GATT handles: clients should discover their peer's attributes. */
#define G2_RING_DEFAULT_WRITE_HANDLE  UINT16_C(0x0010)
#define G2_RING_DEFAULT_NOTIFY_HANDLE UINT16_C(0x0012)
#define G2_RING_DEFAULT_CCCD_HANDLE   UINT16_C(0x0013)
#define G2_RING_TX_WSF_EVENT  UINT8_C(0xac)
/* Logical token bit layout, also usable in a simulator; not an on-air frame. */
static inline uint32_t g2_ring_cccd_token(uint8_t conn, uint8_t final_attempt,
                                         uint16_t epoch) {
    return ((uint32_t)epoch << 16) | ((uint32_t)final_attempt << 8) | conn;
}
#endif
