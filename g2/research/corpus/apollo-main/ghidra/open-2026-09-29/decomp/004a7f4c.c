
undefined4
APP_PbTxEncodeOnboardingHeartbeat
          (undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_54 [12];
  uint local_48;
  int local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  uVar4 = DAT_004a8504;
  uStack_18 = param_4;
  if (param_2 == 0) {
    FUN_00439c04(auStack_40,DAT_004a8530,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a8340,DAT_004a84d4,DAT_004a8534,0xcb,DAT_004a84e8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004a84f0);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004a8504,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_004a8508;
    FUN_0043c0e4(DAT_004a8508,0x10,0);
    *puVar1 = 2;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 4;
    iVar3 = FUN_00443484();
    if ((iVar3 == 1) && (iVar3 = FUN_004434d0(0x10), iVar3 == 1)) {
      puVar1[4] = 0;
    }
    else {
      puVar1[4] = 8;
    }
    cVar2 = FUN_00490c32(auStack_54,DAT_004a8354,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004a8340,DAT_004a84d4,DAT_004a8534,0xe2,DAT_004a850c,local_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004a8510,DAT_004a8510,local_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_004a84d8;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        FUN_0043d574(1,DAT_004a8340,DAT_004a84d4,DAT_004a8534,0xe5,DAT_004a8514,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_004a84d8;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        compress_log_output(0x4400000,DAT_004a8518,DAT_004a8518,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,0x10,uVar4,local_48 & 0xffff);
      uVar4 = 0;
    }
  }
  return uVar4;
}

