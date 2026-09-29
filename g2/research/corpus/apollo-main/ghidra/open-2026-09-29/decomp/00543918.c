
undefined4 PB_RxAudControl(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == 0) {
    FUN_00439c04(&local_20,DAT_00543c08,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_00543c0c;
      local_20 = 0x154;
      FUN_0043d574(1,DAT_00543bf8,DAT_00543bf4,DAT_00543c10);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00543c14,DAT_00543c14);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_00543c18;
      local_20 = 0x158;
      FUN_0043d574(2,DAT_00543bf8,DAT_00543bf4,DAT_00543c10);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00543c1c,DAT_00543c1c);
    }
    uVar2 = 0;
  }
  return uVar2;
}

