/* Private reconstructed ABI; not an application BLE interface. */
#ifndef OPENCFW_PCM22_DEFERRED_NATIVE_H
#define OPENCFW_PCM22_DEFERRED_NATIVE_H
#include <stdint.h>
uint32_t opencfw_pcm22_sequence21b(void);
uint32_t opencfw_pcm22_post_lptohp(void);
/* Raw return follows locked packed-profile word; do not interpret as status. */
uint32_t opencfw_spot_pcm22_transition22(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton);
/* Published major0x20000150, profile words0x20026ba4+4*major,
 * continuation byte0x200271bc, post-hook slot0x20026e60.
 * Body reads published major/profile three times; no immutable ownership. */
#endif
