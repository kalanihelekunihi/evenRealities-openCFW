
undefined4
APP_PbTxEncodeNotifCommResp
          (undefined1 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

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
  
  puVar1 = DAT_004d78fc;
  uStack_18 = param_4;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_004d7910,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d7914,0xa2,DAT_004d76bc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004d76c4);
    }
    uVar4 = 2;
  }
  else {
    FUN_0043c0e4(DAT_004d78fc,0x4c,0);
    *puVar1 = 0xa1;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 5;
    puVar1[4] = *param_2;
    puVar1[5] = param_2[1];
    uVar4 = DAT_004d78f8;
    FUN_004905f4(auStack_2c,DAT_004d78f8,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    cVar2 = FUN_00490c32(auStack_54,DAT_004d76a0,puVar1);
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_004d76a4;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d7914,0xb4,DAT_004d7918,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_004d76a4;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        compress_log_output(0x4400000,DAT_004d791c,DAT_004d791c,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d7694,DAT_004d7690,DAT_004d7914,0xb9,DAT_004d7900,local_48 & 0xffff);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004d7904,DAT_004d7904,local_48 & 0xffff);
      }
      Thread_MsgPbTxByBle(1,4,uVar4,local_48 & 0xffff);
      uVar4 = 0;
    }
  }
  return uVar4;
}

