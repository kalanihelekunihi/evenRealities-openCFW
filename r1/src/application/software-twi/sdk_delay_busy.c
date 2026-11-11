/* Exact software-TWI timing boundary. C supplies the wrapping shift and
 * musttail call; the condition primitive preserves native zero-path flags. */
#include <stdint.h>
extern void r1_rtt_delay_cycles(uint32_t);
void r1_twi_delay_busy(uint32_t us) {
 /* Keep CMP/BEQ: CBZ would leave native zero-path APSR flags unchanged. */
 __asm__ goto("cmp %0,#0\nbeq %l[done]" :: "r"(us) : "cc" : done);
 register void (*target)(uint32_t) __asm__("r1")=r1_rtt_delay_cycles;
 __asm__ volatile("" : "+r"(target));
 __attribute__((musttail)) return target(us<<6);
done:;
}
/* Same stock microsecond contract at BMA 53aa4 and nrfx 7a72c. No extra
 * forwarding frame; retain one C implementation and its flags primitive. */
extern __typeof__(r1_twi_delay_busy) r1_bma_delay_us
 __attribute__((alias("r1_twi_delay_busy")));
extern __typeof__(r1_twi_delay_busy) delay_us
 __attribute__((alias("r1_twi_delay_busy")));
