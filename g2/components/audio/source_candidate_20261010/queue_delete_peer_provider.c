/* Apollo MAIN 0x449BEC: CMSIS queue delete caller contract. */
#include <stdint.h>

extern uint32_t audio_irq_context(void);
extern int32_t audio_queue_delete(void *queue);

int32_t audio_queue_delete_peer(void *queue) {
    if (audio_irq_context()) return -6;
    if (!queue) return -4;
    (void)audio_queue_delete(queue);
    return 0;
}
