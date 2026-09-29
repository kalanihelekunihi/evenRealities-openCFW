
undefined8 APP_SlaveHanderInit(undefined1 param_1,int param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  iVar3 = FUN_0043d0ce();
  local_18 = param_3;
  local_14 = param_4;
  if (iVar3 << 0x1e < 0) {
    local_14 = DAT_0046f3f8;
    local_18 = 0x264;
    FUN_0043d574(4,DAT_0046f404,DAT_0046f400,DAT_0046f3fc);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0046f408,DAT_0046f408);
  }
  *DAT_0046f410 = DAT_0046f40c;
  *DAT_0046f418 = DAT_0046f414;
  piVar1 = DAT_0046f3c4;
  *DAT_0046f3c4 = param_2;
  piVar2 = DAT_0046f41c;
  *DAT_0046f41c = param_3;
  *DAT_0046f420 = *piVar1 + 0x2a;
  *(undefined1 *)(*piVar2 + 0x1f) = 0;
  _bleAdvNameSet();
  ble_msgtx_set_config(param_1,param_2,param_3);
  APP_EvenOtaHandlerInit(param_1);
  APP_BleEusHandlerInit(param_1);
  APP_BleEssHandlerInit(param_1);
  APP_BleEfsHandlerInit(param_1);
  APP_BleNusHandlerInit(param_1);
  profileAnccInit(param_1,param_2,param_3);
  return CONCAT44(local_14,local_18);
}

