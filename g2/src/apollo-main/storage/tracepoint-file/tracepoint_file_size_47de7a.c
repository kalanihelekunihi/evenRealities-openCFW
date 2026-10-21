/* Stock Main 0x47de7a shares the verified positive-size file facade. */
#include <stdint.h>

extern uint32_t audio_tracepoint_file_size_5edb68(const char *);

uint32_t audio_tracepoint_file_size_47de7a(const char *path) {
    return audio_tracepoint_file_size_5edb68(path);
}
