/* R1 registry CONNECTED failure uses a returning diagnostic, not a halt. */
#include "app_error.h"
extern void r1_adc_error(uint32_t);
#undef APP_ERROR_HANDLER
#define APP_ERROR_HANDLER(code) r1_adc_error(code)
