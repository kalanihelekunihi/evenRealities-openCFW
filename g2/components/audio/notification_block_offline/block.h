#ifndef AUDIO_NOTIFICATION_BLOCK_OFFLINE_H
#define AUDIO_NOTIFICATION_BLOCK_OFFLINE_H
#include <stdint.h>
/* Valid current task linked in ready list; coherent sorted delayed lists.
 * Called with scheduler critical mask already raised. No switch is performed. */
void audio_block_current(uint32_t ticks,uint32_t can_block_indefinitely);
#endif
