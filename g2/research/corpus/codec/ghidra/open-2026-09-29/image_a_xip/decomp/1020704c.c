
undefined4 gx8002_audio_input_buffer_addr(int param_1)

{
  undefined4 uVar1;
  
  audio_board_get();
  if (param_1 != 2) {
    if (param_1 == 4) {
      uVar1 = gx8002_logfbank_buffer_addr();
      return uVar1;
    }
    if (param_1 != 1) {
      return 0;
    }
  }
  uVar1 = gx8002_mic_buffer_addr();
  return uVar1;
}

