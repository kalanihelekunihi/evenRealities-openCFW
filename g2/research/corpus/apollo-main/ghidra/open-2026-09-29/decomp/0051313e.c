
undefined4 input_buzzer_start(int param_1)

{
  undefined4 unaff_r7;
  
  DRV_BuzzerPlayAfterQueue(*(undefined4 *)(param_1 + 8));
  return unaff_r7;
}

