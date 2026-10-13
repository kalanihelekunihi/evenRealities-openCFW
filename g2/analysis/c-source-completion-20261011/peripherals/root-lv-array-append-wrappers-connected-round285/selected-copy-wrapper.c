void *audio_uart_lv_grid_copy_454738(void *destination,const void *source,uint32_t length)
{
    (void)audio_queue_copy_bytes(destination,source,length);
    return destination;
}
