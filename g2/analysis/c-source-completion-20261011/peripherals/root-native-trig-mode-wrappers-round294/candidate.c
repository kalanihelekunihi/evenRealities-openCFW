#include <stdint.h>
/* Native math interface consumes angle inS0 and mode inR0; explicit VFP PCS. */
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_core_5094c0(uint32_t,float);
/* Native50968c..509690. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode1_50968c(float angle) {
 return audio_uart_float_trig_core_5094c0(1u,angle);
}
/* Native509690..509694. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode0_509690(float angle) {
 return audio_uart_float_trig_core_5094c0(0u,angle);
}
