
undefined8
DRV_BuzzerPlayAfterQueue(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (param_1 < 9) {
    iVar2 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0x140;
      param_2 = PTR_s_buzzer_play_type__d_00502d30;
      FUN_0043d574(3,DAT_00502cd0,DAT_00502ccc,PTR_s_DRV_BuzzerPlayAfterQueue_00502d28,0x140,
                   PTR_s_buzzer_play_type__d_00502d30,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__drv_buzzer_buzzer_play_type__d_00502d34,
                          PTR_s__drv_buzzer_buzzer_play_type__d_00502d34,param_1);
    }
    _buzzerPlayStop();
    _buzzerPlayStart(PTR_DAT_00502d38 + param_1 * 0x32);
  }
  else {
    iVar1 = FUN_0043d0ce();
    iVar2 = param_1;
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0x13d;
      param_2 = PTR_s_DRV_BuzzerPlayAfterQueue_type_ou_00502d24;
      FUN_0043d574(1,DAT_00502cd0,DAT_00502ccc,PTR_s_DRV_BuzzerPlayAfterQueue_00502d28,0x13d,
                   PTR_s_DRV_BuzzerPlayAfterQueue_type_ou_00502d24,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__drv_buzzer_DRV_BuzzerPlayAfterQ_00502d2c,
                          PTR_s__drv_buzzer_DRV_BuzzerPlayAfterQ_00502d2c);
    }
  }
  return CONCAT44(param_2,iVar2);
}

