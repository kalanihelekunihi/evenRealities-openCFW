/* Native R1 error-log wrapper/getter and recovered millisecond delay contract.
 * Error logging is not a reset/halt. Backend formatters remain real providers. */
#include <stdint.h>
extern void r1_rtt_delay_cycles(uint32_t cycles);
extern uint32_t r1_structured_log_format(uint32_t marker,const char *descriptor,const char *format,...);
extern void nrf_log_frontend_std_1(uint32_t severity_mid,const char *format,uint32_t value);
volatile uint8_t r1_structured_log_mode __attribute__((section(".r1.log.mode"),aligned(1)))=1;
uint32_t r1_structured_log_mode_get(void) { return r1_structured_log_mode; }
/* Stock 0x914f8 stores the low byte of the requested logging mode. */
void r1_structured_log_mode_set(uint32_t mode) {
    r1_structured_log_mode=(uint8_t)mode;
}
void r1_adc_error(uint32_t error) {
    if ((r1_structured_log_mode_get() & 1u) || (r1_structured_log_mode_get() & 4u))
        r1_structured_log_format(UINT32_C(0x04400000),"[RING]Fatal error, error_code: %08x","[RING]Fatal error, error_code: %08x",error);
    if (r1_structured_log_mode_get() & 2u)
        nrf_log_frontend_std_1(UINT32_C(0x001c0001),"Fatal error, error_code: %08x",error);
}
/* Native 0x784f0 invokes the subtract-three primitive with 64000 per ms. */
void r1_st25_delay_ms(uint32_t milliseconds) {
    while (milliseconds!=0) {
        r1_rtt_delay_cycles(64000);
        --milliseconds;
    }
}
