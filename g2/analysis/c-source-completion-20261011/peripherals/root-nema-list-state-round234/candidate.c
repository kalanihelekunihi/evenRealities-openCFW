#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern volatile uint32_t audio_uart_nema_last_submission;
extern volatile uint32_t audio_uart_nema_command_state_20073bf0[];
/* Native51418e..514194. */
int32_t audio_uart_nema_last_cl_id_51418e(void) {return (int32_t)audio_uart_nema_last_submission;}
/* Native514194..51419a: command state offset20, distinct from IRQ completion cell. */
uint32_t audio_uart_nema_last_submission_id_514194(void) {return audio_uart_nema_command_state_20073bf0[5];}
/* Native5144fa..514504: fresh context pointer then bound list word. */
void *audio_uart_nema_cl_get_bound_5144fa(void) {
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)*(volatile uint32_t *)audio_uart_nema_context_cell;
 return (void *)(uintptr_t)context[1];
}
