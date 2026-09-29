
undefined4
APP_PbTxEncodeErrorCode
          (undefined4 param_1,undefined4 param_2,byte param_3,undefined1 param_4,undefined1 param_5)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_3c [12];
  uint local_30;
  int local_2c;
  undefined1 auStack_28 [20];
  
  uVar4 = DAT_004d8f34;
  FUN_004905f4(auStack_28,DAT_004d8f34,0x100);
  FUN_00439c04(auStack_3c,auStack_28,0x14);
  puVar1 = DAT_004d8efc;
  *DAT_004d8efc = 10;
  *(ushort *)(puVar1 + 2) = (ushort)param_3;
  *(undefined2 *)(puVar1 + 4) = 9;
  puVar1[8] = param_4;
  puVar1[9] = param_5;
  cVar2 = FUN_00490c32(auStack_3c,DAT_004d8ef4);
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f3c,0x148,DAT_004d8f38,local_30);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004d8f40,DAT_004d8f40,local_30);
  }
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar3 = DAT_004d8ef8;
      if (local_2c != 0) {
        iVar3 = local_2c;
      }
      FUN_0043d574(1,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f3c,0x14b,DAT_004d8f44,iVar3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      iVar3 = DAT_004d8ef8;
      if (local_2c != 0) {
        iVar3 = local_2c;
      }
      compress_log_output(0x4400000,DAT_004d8f48,DAT_004d8f48,iVar3);
    }
    uVar4 = 0x2b;
  }
  else {
    Thread_MsgPbTxByBle(1,0x80,uVar4,local_30 & 0xffff);
    uVar4 = 0;
  }
  return uVar4;
}

