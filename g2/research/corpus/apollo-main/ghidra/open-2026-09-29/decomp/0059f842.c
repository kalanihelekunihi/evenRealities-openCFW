
undefined4 APP_PbTranslateTxEncodeCommResp(undefined1 *param_1,undefined1 param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_3c [12];
  uint local_30;
  int local_2c;
  undefined1 auStack_28 [20];
  
  puVar1 = DAT_0059fab4;
  if (param_1 == (undefined1 *)0x0) {
    iVar3 = FUN_0043d0ce(0);
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059fa74,DAT_0059fa70,DAT_0059fac8,0x80,DAT_0059fac4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0059facc);
    }
    uVar4 = 6;
  }
  else {
    FUN_0043c0e4(DAT_0059fab4,0x854,0);
    *puVar1 = 0xa2;
    puVar1[1] = param_2;
    *(undefined2 *)(puVar1 + 2) = 7;
    puVar1[4] = *param_1;
    uVar4 = DAT_0059fab8;
    FUN_004905f4(auStack_28,DAT_0059fab8,0x100);
    FUN_00439c04(auStack_3c,auStack_28,0x14);
    cVar2 = FUN_00490c32(auStack_3c,DAT_0059fa80,puVar1);
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_0059fa84;
        if (local_2c != 0) {
          iVar3 = local_2c;
        }
        FUN_0043d574(1,DAT_0059fa74,DAT_0059fa70,DAT_0059fac8,0x8d,DAT_0059fabc,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_0059fa84;
        if (local_2c != 0) {
          iVar3 = local_2c;
        }
        compress_log_output(0x4400000,DAT_0059fac0,DAT_0059fac0,iVar3);
      }
      uVar4 = 5;
    }
    else {
      FUN_0043dacc(DAT_0059fad0,0x10,uVar4,local_30 & 0xffff);
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        Thread_MsgPbTxByBle(1,5,uVar4,local_30 & 0xffff);
      }
      uVar4 = 0;
    }
  }
  return uVar4;
}

