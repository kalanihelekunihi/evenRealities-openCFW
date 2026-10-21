/* Native 0x43f648 marks object and screen dirty, then schedules LV display
 * event 0x38 through the actual display event provider. */
#include <stdint.h>
extern void *audio_uart_lv_object_screen(void *); /* selected 0x44dbc4 */
extern void *audio_uart_lv_display_for_object(void *); /* selected 0x44dc0a */
extern uint32_t audio_uart_lv_display_event_44fdbe(void *,uint32_t,void *);
void audio_uart_lv_mark_layout_43f648(void *object) {
    uint8_t *obj=(uint8_t *)object;
    uint16_t bits;__builtin_memcpy(&bits,obj+0x2au,2u);
    bits|=1u;__builtin_memcpy(obj+0x2au,&bits,2u);
    uint8_t *screen=(uint8_t *)audio_uart_lv_object_screen(object);
    __builtin_memcpy(&bits,screen+0x2au,2u);
    bits|=4u;__builtin_memcpy(screen+0x2au,&bits,2u);
    void *display=audio_uart_lv_display_for_object(screen);
    (void)audio_uart_lv_display_event_44fdbe(display,0x38u,0);
}
