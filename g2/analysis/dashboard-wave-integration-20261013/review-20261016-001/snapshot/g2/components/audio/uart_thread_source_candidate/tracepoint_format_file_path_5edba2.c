/* Stock Main tracepoint file path formatter at 0x5edba2. */
#include <stdint.h>
extern int32_t g2_audio_dump_snprintf(char *,uint32_t,const char *,...);
void audio_tracepoint_format_file_path_5edba2(char *output,uint32_t capacity,
                                                uint32_t sequence)
{
    (void)g2_audio_dump_snprintf(output,capacity,"/log/tp/tp_%u.bin",sequence);
}
