/* Experimental soft-float ABI adapter to selected C classify body.
 * Selected caller passes IEEE-754 float bits in R0; this C signature preserves
 * that call ABI. Stock original uses hard-float S0, compared separately. */
#include <stdint.h>
extern uint32_t audio_platform_classify(float);
uint32_t callback_classify(float value) {
    return audio_platform_classify(value);
}
