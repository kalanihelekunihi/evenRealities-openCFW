
undefined4 buzzer_beep_start(undefined4 param_1,undefined1 param_2)

{
  undefined4 unaff_r7;
  
  buzzer_pwm_update(param_1,param_2);
  buzzer_pwm_start();
  return unaff_r7;
}

