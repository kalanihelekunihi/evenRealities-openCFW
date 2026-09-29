
undefined4 _buzzerPlayStop(void)

{
  undefined4 unaff_r7;
  
  osTimerStop(*DAT_00502cd8);
  buzzer_beep_stop(1);
  *DAT_00502cb4 = 0;
  *DAT_00502cb8 = 0;
  *DAT_00502cbc = 0;
  return unaff_r7;
}

