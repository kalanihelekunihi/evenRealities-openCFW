/* Apollo Nema signed 16.16 conversion at native 0x5242cc. */
#include <stdint.h>
int32_t audio_uart_nema_float_fixed_5242cc(float value)
    __attribute__((pcs("aapcs-vfp")));
int32_t audio_uart_nema_float_fixed_5242cc(float value) {
    return (int32_t)(value * 65536.0f + 0.5f);
}
