/* Native callback_mgr_delete_node 0x5100fc. */
extern void audio_file_heap_free(void *); /* 0x474d16 */
void audio_callback_mgr_delete_node(void *node) {
    if(node!=0) audio_file_heap_free(node);
}
