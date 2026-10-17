/* Stock GX8002 receive scratch starts at 0x2007397c. The selected send path
 * passes capacity 30, and the next known TX packet starts at 0x2007399c.
 * This source owns only the 30-byte receive span. */
#include <stdint.h>

__attribute__((used, section(".g2_transaction_transport_2007397c"), aligned(4)))
uint8_t g2_audio_transaction_transport[30];

_Static_assert(sizeof g2_audio_transaction_transport == 30u,
               "GX8002 receive capacity");
