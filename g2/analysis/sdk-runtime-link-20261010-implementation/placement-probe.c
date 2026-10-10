#include <stdint.h>
#include "am_util_stdio.h"
/* Compile/link-only section markers. No reset handler, vector, or hardware seam. */
__attribute__((section(".stack"),aligned(8))) unsigned char probe_stack[128];
__attribute__((section(".heap"),aligned(8))) unsigned char probe_heap[128];
__attribute__((section(".shared"))) volatile uint32_t probe_shared;
volatile uint32_t probe_data=0x12345678;
volatile uint32_t probe_bss;
__attribute__((section(".itcm_text"),noinline)) uint32_t probe_itcm(void){return probe_data;}
void placement_probe(void){probe_bss=am_util_stdio_printf("ABI %u %f",1u,1.25);probe_shared=probe_itcm();}
