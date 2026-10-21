/* LittleFS allocator free wrapper, stock 0x4ca812. */
extern void audio_file_heap_free(void *buffer); /* stock 0x474d16 */
void g2_lfs_free(void *buffer) { audio_file_heap_free(buffer); }
