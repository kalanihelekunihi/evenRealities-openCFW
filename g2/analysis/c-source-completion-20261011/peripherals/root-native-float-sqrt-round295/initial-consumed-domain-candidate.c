#include <stdint.h>
extern volatile uint32_t audio_uart_float_math_error_cell_20074f14;
/* Native439ca4..439cb2 andshared439cbe..439cc4: consumed void domain store. */
void audio_uart_float_domain_error_439ca4(void) {
 audio_uart_float_math_error_cell_20074f14=33u;
}
/* Native4397a8..4397c4: explicit architectural FPU instructions, no opcode data. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_sqrt_4397a8(float value) {
 uint32_t status;
 __asm__ volatile("vcmpe.f32 %1, #0.0\n\tvmrs %0, fpscr" : "=r"(status) : "t"(value));
 if(status&0x80000000u) {
  union {uint32_t bits;float value;} result={.bits=0x7fffffffu};
  audio_uart_float_domain_error_439ca4();
  return result.value;
 }
 float result;
 __asm__ volatile("vsqrt.f32 %0, %1" : "=t"(result) : "t"(value));
 return result;
}
