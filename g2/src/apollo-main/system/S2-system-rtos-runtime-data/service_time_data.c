/* Time-sync service ROM tables (a-03-service-time/service_time_sync.c).
 * Bytes from the stock image (VA = file offset + 0x437fe0). */
#include <stdint.h>

typedef struct {
    uint8_t header[4]; /* +0  80 00 08 00 */
    uint8_t role;      /* +4 */
    uint8_t peer_role; /* +5 */
    uint8_t pad[2];    /* +6 */
    uint32_t epoch;    /* +8 */
    int32_t zone;      /* +12 */
} g2_time_sync_record_t;
_Static_assert(sizeof(g2_time_sync_record_t) == 16u, "time sync record");

/* ROM 0x788f10: 80 00 08 00, then 12 zero bytes. */
const g2_time_sync_record_t g2_time_sync_template = {{0x80u, 0x00u, 0x08u, 0x00u}, 0u, 0u, {0u, 0u}, 0u, 0};

/* ROM 0x7717a8: seven pointers to ROM 0x78f3d0.."Sat" (4-byte stride). */
const char *const g2_time_weekday_names[7] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
