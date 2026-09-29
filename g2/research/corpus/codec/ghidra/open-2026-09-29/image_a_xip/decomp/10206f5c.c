
uint gx8002_pcm_frame_size(void)

{
  return (uint)(*(int *)(DAT_10206f70 + 0x1c) * *(int *)(DAT_10206f70 + 0x20)) / 1000;
}

