/* Native WsfQueueEnq 0x538c24 and WsfCsEnter/Exit 0x52b8a4/b6. */
#include <stdint.h>
extern volatile uint8_t audio_wsf_cs_depth; /* live RAM */
void WsfCsEnter(void) {
    if(audio_wsf_cs_depth==0u)
        __asm volatile("cpsid i" ::: "memory");
    audio_wsf_cs_depth++;
}
void WsfCsExit(void) {
    audio_wsf_cs_depth--;
    if(audio_wsf_cs_depth==0u)
        __asm volatile("cpsie i" ::: "memory");
}

/* Former duplicate bodies (ble/wsf-cs/display_wsf_cs.c) now bind here. */
__typeof__(WsfCsEnter) audio_wsf_cs_enter __attribute__((alias("WsfCsEnter")));
__typeof__(WsfCsExit) audio_wsf_cs_exit __attribute__((alias("WsfCsExit")));
