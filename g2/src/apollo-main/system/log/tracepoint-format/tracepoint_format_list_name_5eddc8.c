/* Stock Main 0x5eddc8: render a tracepoint sequence in a bounded list slot. */
#include <stdint.h>
extern int32_t g2_audio_dump_snprintf(char *,uint32_t,const char *,...);

int32_t audio_tracepoint_format_list_name_5eddc8(uint32_t sequence,uint32_t role,
                                                  char *output,uint32_t capacity) {
    if(output==0 || capacity==0u || sequence==0u) return 0;
    return g2_audio_dump_snprintf(output,capacity,"%c:%c%u",
                                  role&0xffu,(uint32_t)'t',sequence);
}
