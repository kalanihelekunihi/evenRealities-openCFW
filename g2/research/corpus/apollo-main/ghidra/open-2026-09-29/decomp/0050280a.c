
void buzzer_beep_stop(char param_1)

{
  buzzer_pwm_stop();
  if (param_1 != '\0') {
    FUN_00480f0c(0x91,*DAT_00502cb0);
  }
  return;
}

