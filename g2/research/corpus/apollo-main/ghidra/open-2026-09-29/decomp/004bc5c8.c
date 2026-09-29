
undefined4
PB_TxEncodeBleConnectParams
          (byte param_1,int param_2,undefined2 param_3,undefined1 *param_4,int param_5)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_7c [12];
  uint local_70;
  int local_6c;
  undefined1 auStack_68 [4];
  undefined2 local_64;
  undefined1 auStack_54 [4];
  undefined2 local_50;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  
  uVar2 = 0;
  if (param_2 == 0) {
    FUN_00439c04(auStack_40,DAT_004bcdec,0x14);
    local_3c = 1;
    uVar2 = APP_errorFaultHandler(auStack_40);
  }
  if (param_4 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_54,DAT_004bcdf0,0x14);
    local_50 = 1;
    uVar2 = APP_errorFaultHandler(auStack_54);
  }
  if (param_5 == 0) {
    FUN_00439c04(auStack_68,DAT_004bcdf4,0x14);
    local_64 = 1;
    uVar2 = APP_errorFaultHandler(auStack_68);
  }
  if (((param_2 == 0) || (param_4 == (undefined1 *)0x0)) || (param_5 == 0)) {
    iVar3 = FUN_0043d0ce(uVar2);
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcdf8,0x1fe,DAT_004bc914);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004bc91c,DAT_004bc91c);
    }
    uVar2 = 2;
  }
  else {
    FUN_0043c0e4(param_2,param_3,0);
    FUN_004905f4(auStack_2c,param_2,param_3);
    FUN_00439c04(auStack_7c,auStack_2c,0x14);
    *param_4 = 7;
    *(ushort *)(param_4 + 2) = (ushort)param_1;
    *(undefined2 *)(param_4 + 4) = 6;
    param_4[0xe] = 0;
    cVar1 = FUN_00490c32(auStack_7c,DAT_004bc920,param_4);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcdf8,0x20e,DAT_004bc924,local_70);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004bc928,DAT_004bc928,local_70);
    }
    if (cVar1 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_004bc92c;
        if (local_6c != 0) {
          iVar3 = local_6c;
        }
        FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcdf8,0x211,DAT_004bc930,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_004bc92c;
        if (local_6c != 0) {
          iVar3 = local_6c;
        }
        compress_log_output(0x4400000,DAT_004bcb04,DAT_004bcb04,iVar3);
      }
      uVar2 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,0x80,param_2,local_70 & 0xffff);
      uVar2 = 0;
    }
  }
  return uVar2;
}

