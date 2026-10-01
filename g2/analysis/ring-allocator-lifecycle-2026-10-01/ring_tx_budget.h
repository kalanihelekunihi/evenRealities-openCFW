/* Host analysis helpers, not a firmware patch or proof of free pool capacity.
 * Limits recovered from s200_v2.2.6.10; explicit size arithmetic avoids the
 * stock allocator's 16-bit wrap. No connection or scheduler state is modeled. */
#ifndef OPENCFW_RING_TX_BUDGET_H
#define OPENCFW_RING_TX_BUDGET_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
static inline unsigned g2_wsf_message_class(size_t message_bytes) {
 if(message_bytes>472)return 0;
 size_t total=message_bytes+8;
 return total<=16?16:total<=32?32:total<=64?64:480;
}
/* header_bytes=12 for existing shape, or e.g. 16 for an enlarged proposal.
 * mtu is the actual negotiated ATT MTU, not a guessed ring default. */
static inline bool g2_ring_inline_budget(size_t payload_bytes,size_t header_bytes,
                                         uint16_t mtu,unsigned *message_class) {
 if(header_bytes<12 || header_bytes>472 || payload_bytes>472-header_bytes ||
    payload_bytes>461 || mtu<3 || payload_bytes>(size_t)mtu-3)return false;
 if(message_class)*message_class=g2_wsf_message_class(header_bytes+payload_bytes);
 return true;
}
#endif
