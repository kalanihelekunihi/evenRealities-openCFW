
undefined8 FUN_00471608(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_00471b2c;
  if (*DAT_00471b2c == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = *DAT_00471ae8;
      param_1 = 0xd1;
      param_2 = DAT_00471b30;
      FUN_0043d574(3,DAT_00471ae0,DAT_00471adc,DAT_00471b34,0xd1,DAT_00471b30,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00471b38,DAT_00471b38,*DAT_00471ae8,param_1,param_2,param_3)
      ;
    }
    iVar2 = SVC_KvdbWriteDashboardAutoCloseValue(*DAT_00471ae8);
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0xd4;
        param_2 = DAT_00471b3c;
        FUN_0043d574(1,DAT_00471ae0,DAT_00471adc,DAT_00471b34);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__general_configure_DashboardAuto_00471b40);
      }
    }
    *piVar1 = 0;
  }
  return CONCAT44(param_2,param_1);
}

