void audio_uart_lv_basic_box_clear_454746(void *box,uint32_t fill,uint32_t size)
{
    audio_uart_buffer_zero(box,size,(uint8_t)fill);
}