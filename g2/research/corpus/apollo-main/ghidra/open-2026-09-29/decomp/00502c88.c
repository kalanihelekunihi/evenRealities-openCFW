
undefined4
DRV_BuzzerStart(undefined4 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  _buzzerPlayStop();
  FUN_00480f0c(0x91,*DAT_00502d0c);
  buzzer_beep_start(param_1,param_2);
  return param_4;
}

