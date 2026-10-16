/* Tracepoint caller name for the stock file-open facade at 0x474550. */
#include <stdint.h>

extern void *audio_file_open(const char *path, const char *mode);

void *audio_tracepoint_file_open_474550(const char *path, const char *mode) {
    return audio_file_open(path, mode);
}
