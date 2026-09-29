
undefined4
PB_RxGlassesCaseInfo(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_c;
  
  if (param_2 == 0) {
    uStack_c = param_4;
    FUN_00439c04(&local_20,DAT_00510f9c,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_00510fa0;
      local_20 = 0x58;
      FUN_0043d574(1,DAT_00510f68,DAT_00510f64,DAT_00510fa4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510fa8,DAT_00510fa8);
    }
    uVar2 = 2;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

