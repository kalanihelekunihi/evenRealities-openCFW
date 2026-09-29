
void gx8002_audio_input_standby_startup(void)

{
  *(byte *)(DAT_1020767c + 0x10) = *(byte *)(DAT_1020767c + 0x10) & 0xf | 0x10;
  gx_audio_in_set_interrupt_enable(0x30007);
  return;
}

