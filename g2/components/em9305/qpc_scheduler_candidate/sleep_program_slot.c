/* Native 0x31377c..0x3137f4. Timer-program wrapper has incidental
 * R0 return 0xf00844, independent from the programmed deadline. */
#include <stdint.h>
uint32_t opencfw_em9305_sleep_write_slot(uint32_t index,uint32_t value)
{
 uint32_t irq; __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 volatile uint8_t *enabled=(volatile uint8_t *)(uintptr_t)0xf00464u;
 uint32_t saved=*enabled,mask=*enabled;
 __asm__ volatile("bclr %0,%0,%1" : "+r"(mask) : "r"(index));
 *enabled=(uint8_t)(mask&15u);
 *(volatile uint32_t *)(uintptr_t)(0xf00468u+index*4u)=value;
 uint32_t current=*enabled,result=(saved&15u)|current;
 *enabled=(uint8_t)result;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return result;
}
uint32_t opencfw_em9305_sleep_program_slot(uint32_t value,uint32_t index,uint32_t incoming_r2,uint32_t incoming_r3)
{
 (void)incoming_r2;(void)incoming_r3;
 (void)opencfw_em9305_sleep_write_slot(index,value);
 volatile uint8_t *enabled=(volatile uint8_t *)(uintptr_t)0xf00464u;
 uint32_t bit=1;
 uint32_t old=*enabled;
 __asm__ volatile("asl %0,%0,%1" : "+r"(bit) : "r"(index));
 bit&=15u;
 *enabled=(uint8_t)(old|bit);
 volatile uint8_t *pending=(volatile uint8_t *)(uintptr_t)0xf00466u;
 *pending=(uint8_t)(*pending|bit);
 *(volatile uint32_t *)(uintptr_t)0xf00844u=bit;
 __asm__ volatile("sync" ::: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf00834u=bit;
 *(volatile uint32_t *)(uintptr_t)0xf00828u=bit;
 return 0xf00844u;
}
