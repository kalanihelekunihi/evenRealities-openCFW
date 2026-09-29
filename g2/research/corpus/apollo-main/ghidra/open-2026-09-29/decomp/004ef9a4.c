
undefined8 FUN_004ef9a4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_004efa64;
  if (*DAT_004efa64 != 0) {
    ui_common_api_fn_00509c96(*DAT_004efa64);
    *piVar1 = 0;
  }
  iVar2 = ui_common_api_fn_00509c1c();
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x4e8;
      FUN_0043d574(1,DAT_004eff18,DAT_004eff14,DAT_004eff10,0x4e8,DAT_004eff0c,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004eff1c,DAT_004eff1c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *DAT_004efa5c = 0;
    *DAT_004efa6c = 0;
    *DAT_004efa70 = 0;
    *DAT_004efa50 = 0;
    *DAT_004efef0 = 0;
    *DAT_004efef4 = 0;
    FUN_004eef7c(param_1);
    *DAT_004eff20 = 1;
    FUN_00500180(0);
    uVar3 = 0;
  }
  return CONCAT44(param_2,uVar3);
}

