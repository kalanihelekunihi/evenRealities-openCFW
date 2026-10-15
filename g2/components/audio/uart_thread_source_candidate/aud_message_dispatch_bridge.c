/* Native 0x53c638 is the selected AUD_SendMessage C provider. */
extern void stock_audio_submit(const void *message);

void audio_aud_message_dispatch_53c638(const void *message) {
    stock_audio_submit(message);
}
