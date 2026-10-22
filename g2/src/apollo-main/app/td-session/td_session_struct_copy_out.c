/* Apollo session structure copy-out, native 0x597be4. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];

/* Stock 0x597BE4 (td_session_struct_copy_out) */
uint32_t audio_td_session_struct_copy_out(const void *source) {
    if(source==0) return UINT32_MAX;
    const uint8_t *p=source;
    for(uint32_t i=0;i<0x84cu;++i) audio_td_state[0x808u+i]=p[i];
    return 0u;
}
