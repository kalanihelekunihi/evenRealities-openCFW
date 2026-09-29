
int audio_board_gain(int param_1)

{
  int iVar1;
  
  if (param_1 - 1U < 9) {
    iVar1 = (int)(char)PTR_gx8002_messages_gain_10203020[param_1 - 1U];
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

