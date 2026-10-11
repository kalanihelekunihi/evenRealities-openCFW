/* Native WsfCsEnter/Exit 0x52b8a4/0x52b8b6, including CPSID/CPSIE. */
#include <stdint.h>
extern volatile uint8_t audio_wsf_cs_depth; /* RAM 0x20075045 */
void audio_wsf_cs_enter(void) {
    if(audio_wsf_cs_depth==0u) __asm__ volatile("cpsid i" ::: "memory");
    audio_wsf_cs_depth=(uint8_t)(audio_wsf_cs_depth+1u);
}
void audio_wsf_cs_exit(void) {
    audio_wsf_cs_depth=(uint8_t)(audio_wsf_cs_depth-1u);
    if(audio_wsf_cs_depth==0u) __asm__ volatile("cpsie i" ::: "memory");
}
