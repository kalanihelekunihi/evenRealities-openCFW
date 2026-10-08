/* Locked f89a4c46 reconstruction:429da4..429df6 and42a036..42a04a.
 * No scheduler, allocation or cancellation token is implied by the byte guard. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
uint32_t opencfw_pcm22_sequence21b(void){
 uint32_t t=W(0x20026ba4+4*W(0x20000150));
 W(0x40020080)=(W(0x40020080)&~0x3c00u)|(((t>>17)&15)<<10);
 t=W(0x20026ba4+4*W(0x20000150));
 W(0x40020080)=(W(0x40020080)&~1023u)|((t>>7)&1023u);
 t=W(0x20026ba4+4*W(0x20000150));
 W(0x40020044)=(W(0x40020044)&~127u)|((t>>21)&127u);
 B(0x200271bc)=0;return 0;
}
uint32_t opencfw_pcm22_post_lptohp(void){
 if(B(0x200271bc)) (void)opencfw_pcm22_sequence21b();
 return 0;
}
