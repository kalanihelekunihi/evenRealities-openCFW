
int gx8002_audio_input_buffer_size(int param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (param_1 == 2) {
    uVar2 = gx8002_mic_buffer_size();
    uVar3 = gx8002_mic_channel_count();
    iVar1 = (uVar2 / uVar3) * 2;
  }
  else if (param_1 == 4) {
    iVar1 = gx8002_logfbank_buffer_size();
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

