#ifndef AUDIO_CLOCK_TIMING_H
#define AUDIO_CLOCK_TIMING_H
#include <stdint.h>
uint32_t audio_save_irq(void);
/* Spin body requires a positive count. Stock zero underflows into 2^32 loops.
 * Native delay only enters it after overhead subtraction leaves count>0. */
void audio_delay_cycles(uint32_t count);
void audio_delay_us(uint32_t microseconds);
/* Addresses must refer to valid mapped readable words. Poll before delaying;
 * return0 on condition,4 on exhausted delay budget. fifth arg narrows to byte. */
uint32_t audio_wait4(uint32_t budget,uint32_t address,uint32_t mask,uint32_t expected);
uint32_t audio_wait5(uint32_t budget,uint32_t address,uint32_t mask,uint32_t expected,uint32_t equal);
#endif
