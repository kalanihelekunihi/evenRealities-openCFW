
undefined4 APP_PbTelepromptTxEncodeCommResp(undefined1 param_1,undefined1 *param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_3c [12];
  uint local_30;
  int local_2c;
  undefined1 auStack_28 [20];
  
  puVar1 = DAT_00588d34;
  FUN_0043c0e4(DAT_00588d34,0xf58,0);
  *puVar1 = 0xa6;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 0xc;
  puVar1[4] = *param_2;
  uVar4 = DAT_00588d38;
  FUN_004905f4(auStack_28,DAT_00588d38,0x100);
  FUN_00439c04(auStack_3c,auStack_28,0x14);
  cVar2 = FUN_00490c32(auStack_3c,DAT_00588d0c,puVar1);
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar3 = DAT_00588d10;
      if (local_2c != 0) {
        iVar3 = local_2c;
      }
      FUN_0043d574(1,DAT_00588d00,DAT_00588cfc,DAT_00588d40,0x6a,DAT_00588d3c,iVar3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      iVar3 = DAT_00588d10;
      if (local_2c != 0) {
        iVar3 = local_2c;
      }
      compress_log_output(0x4400000,DAT_00588d44,DAT_00588d44,iVar3);
    }
    uVar4 = 0x2b;
  }
  else {
    FUN_0043dacc(DAT_00588d48,0x10,uVar4,local_30 & 0xffff);
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      Thread_MsgPbTxByBle(1,6,uVar4,local_30 & 0xffff);
    }
    uVar4 = 0;
  }
  return uVar4;
}

