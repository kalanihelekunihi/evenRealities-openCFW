void audio_uart_lv_array_clear_488478(void *array) {
    volatile uint8_t *a=array;
    volatile uint32_t *words=array;
    if(words[0]!=0u) {
        if(a[16u]!=0u)audio_uart_lv_heap_free((void *)(uintptr_t)words[0]);
        words[0]=0u;
    }
    words[1]=0u;words[2]=0u;
}
