
undefined4 PB_RxQuickRestart(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == 0) {
    FUN_00439c04(&local_20,DAT_005439dc,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_005436d4;
      local_20 = 0xae;
      FUN_0043d574(1,DAT_005436e0,DAT_005436dc,DAT_005439e0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005436e4,DAT_005436e4);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_00543b8c;
      local_20 = 0xb2;
      FUN_0043d574(4,DAT_005436e0,DAT_005436dc,DAT_005439e0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00543b90,DAT_00543b90);
    }
    FUN_0044b0ae();
    uVar2 = 0;
  }
  return uVar2;
}

