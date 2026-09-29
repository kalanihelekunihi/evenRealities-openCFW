
undefined4 PB_RxRestoreFactory(undefined4 param_1,int param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 local_20 [4];
  undefined1 auStack_1c [4];
  undefined2 local_18;
  
  if (param_2 == 0) {
    FUN_00439c04(auStack_1c,DAT_005436d0,0x14);
    local_18 = 1;
    APP_errorFaultHandler(auStack_1c);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005436e0,DAT_005436dc,DAT_005436d8,0x5c,DAT_005436d4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005436e4);
    }
    uVar3 = 2;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005436e0,DAT_005436dc,DAT_005436d8,0x60,DAT_005436e8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005436ec);
    }
    cVar1 = FUN_0045a568();
    iVar2 = FUN_00443484();
    if (iVar2 == 1) {
      iVar2 = FUN_0044349c();
      if (iVar2 == 1) {
        if (cVar1 == '\x01') {
          FUN_00464c36(0,0,0,0);
        }
        osDelay(500);
      }
      iVar2 = FUN_004434b4();
      if (iVar2 == 1) {
        if (cVar1 == '\x01') {
          FUN_00464c36(0,0,0,0);
        }
        osDelay(500);
      }
    }
    SVC_KvdbInvalidateMagic();
    local_20[0] = 1;
    kvdbOnboardingConfigUpdateAndPersist(0,local_20);
    file_remove(DAT_00543908);
    FUN_004b46ce();
    iVar2 = FUN_004761d2();
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005436e0,DAT_005436dc,DAT_005436d8,0x7c,DAT_0054390c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005439bc);
      }
    }
    FUN_0044b0ae();
    uVar3 = 0;
  }
  return uVar3;
}

