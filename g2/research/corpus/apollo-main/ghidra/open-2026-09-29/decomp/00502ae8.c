
undefined8
DRV_BuzzerInit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  buzzer_pwm_config(7,0,1000,0x1e);
  piVar1 = DAT_00502cd8;
  iVar2 = osTimerNew(DAT_00502d14,0,0,DAT_00502d10);
  *piVar1 = iVar2;
  local_10 = param_3;
  local_c = param_4;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_00502d18;
      local_10 = 300;
      FUN_0043d574(1,DAT_00502cd0,DAT_00502ccc,DAT_00502d1c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__drv_buzzer__buzzerPwmGpioInit_o_00502d20);
    }
  }
  return CONCAT44(local_c,local_10);
}

