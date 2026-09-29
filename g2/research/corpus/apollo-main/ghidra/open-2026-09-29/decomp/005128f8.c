
undefined8 FUN_005128f8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_0055eff0(DAT_00512b14,0);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x4c7;
      param_2 = DAT_00512c40;
      FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,DAT_00512c44,0x4c7,DAT_00512c40,param_3
                   ,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00512c48,DAT_00512c48);
    }
  }
  else {
    iVar1 = FUN_0055f0d8(iVar1,0xf);
    if (iVar1 != DAT_00512c1c) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x4d3;
        param_2 = DAT_00512c4c;
        FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,DAT_00512c44,0x4d3,DAT_00512c4c,iVar1
                     ,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00512c50,DAT_00512c50,iVar1);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

