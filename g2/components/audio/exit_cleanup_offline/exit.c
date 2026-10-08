/* Selected logger-disabled exit flow; actual request and OS peers.
 * No producer-stop acknowledgement or queue-drain is supplied here. */
#include <stdint.h>
extern void audio_exit_request(uint32_t);
extern uint32_t audio_timer_stop(uint32_t),audio_timer_delete(uint32_t),audio_queue_delete(uint32_t),audio_delay(uint32_t);
void audio_exit_logger_disabled(void){
 audio_exit_request(3);
 volatile uint32_t *timer=(volatile uint32_t *)0x20074a98u,*queue=(volatile uint32_t *)0x20003fa4u;
 if(*timer){(void)audio_timer_stop(*timer);(void)audio_timer_delete(*timer);*timer=0;}
 if(*queue){(void)audio_queue_delete(*queue);*queue=0;}
 for(;;)(void)audio_delay(0xffffffffu);
}
