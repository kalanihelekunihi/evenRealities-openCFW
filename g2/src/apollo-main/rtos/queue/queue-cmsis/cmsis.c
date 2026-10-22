/* Offline stock CMSIS/FreeRTOS wrapper reconstruction, not pristine-public attribution. */
/* audio_scheduler_state, audio_cmsis_irq_context and audio_cmsis_queue_put
 * (stock 0x4558A4, 0x44900E, 0x449ABE) are now compiled from upstream
 * FreeRTOS tasks.c / CMSIS-FreeRTOS cmsis_os2.c; their old names are payload
 * defsyms (U4-freertos). */
#include <stdint.h>

/* Queue-buffer copy contract: valid nonoverlapping regions, no libc/original helper. */
void *audio_queue_copy_bytes(void *destination,const void *source,uint32_t size){
 uint8_t *d=destination;const uint8_t *s=source;
 for(uint32_t i=0;i<size;i++)d[i]=s[i];return destination;
}
