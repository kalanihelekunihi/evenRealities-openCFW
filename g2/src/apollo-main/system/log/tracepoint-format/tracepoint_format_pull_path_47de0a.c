/* Stock Main 0x47de0a: format a tracepoint sequence path. */
#include <stdint.h>

extern int32_t g2_audio_dump_snprintf(char *,uint32_t,const char *,...);

void audio_tracepoint_format_pull_path_47de0a(char *output,uint32_t capacity,uint32_t sequence) {
    (void)g2_audio_dump_snprintf(output,capacity,"/log/tp/tp_%u.bin",sequence);
}
