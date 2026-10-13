void audio_uart_lv_array_clear_488478(void *array) {
    uint8_t *a=(uint8_t *)array;
    void *data=*(void **)(void *)a;
    if(data!=0) {
        if(a[0x10u]!=0u)audio_uart_lv_heap_free(data);
        *(uint32_t *)(void *)a=0u;
    }
    *(uint32_t *)(void *)(a+4u)=0u;
    *(uint32_t *)(void *)(a+8u)=0u;
}
