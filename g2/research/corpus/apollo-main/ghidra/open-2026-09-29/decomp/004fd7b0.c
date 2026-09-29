
undefined8 FUN_004fd7b0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_004fd918;
  if (*DAT_004fd918 != 0) {
    ui_common_api_fn_00509c96(*DAT_004fd918);
    *piVar1 = 0;
  }
  iVar2 = ui_common_api_fn_00509c1c();
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x65f;
      FUN_0043d574(1,DAT_004fd928,DAT_004fd924,DAT_004fd920,0x65f,DAT_004fd91c,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004fd92c,DAT_004fd92c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *DAT_004fd930 = 0;
    piVar1 = DAT_004fd910;
    *DAT_004fd910 = 0;
    FUN_004fc644(param_1);
    *DAT_004fd934 = 1;
    FUN_0050029c(*piVar1 + 1);
    uVar3 = 0;
  }
  return CONCAT44(param_2,uVar3);
}

