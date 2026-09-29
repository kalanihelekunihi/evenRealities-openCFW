
undefined4 buzzer_play_next(void)

{
  undefined4 unaff_r7;
  
  if (*DAT_00502cb4 != 0) {
    _buzzerPlayVoice();
  }
  return unaff_r7;
}

