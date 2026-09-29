
int gx8002_aout_get_mute(int param_1)

{
  return (int)*(short *)(param_1 + 0x10);
}

