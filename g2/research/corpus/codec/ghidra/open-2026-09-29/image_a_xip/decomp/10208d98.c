
void audio_range_callback(int param_1,int param_2)

{
  int iStack_c;
  uint uStack_8;
  
  iStack_c = param_2 + 1;
  uStack_8 = (param_2 * 2 - param_1) + 1;
  if (*DAT_10208dc8 <= uStack_8) {
    uStack_8 = param_2 - param_1;
    iStack_c = 0;
  }
  gx8002_audio_out_push_frame(DAT_10208dc8[1],&iStack_c);
  return;
}

