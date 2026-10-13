/* Public caller names for existing canonical heap bodies474cd2/474d16. */
#include <stdint.h>
extern void *codec_allocate(uint32_t);
extern void audio_file_heap_free(void *);
void *file_heap_allocate(uint32_t bytes) { return codec_allocate(bytes); }
void file_heap_free(void *buffer) { audio_file_heap_free(buffer); }
