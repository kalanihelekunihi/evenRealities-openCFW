
int FUN_004da078(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_44 [12];
  uint local_38;
  int local_34;
  undefined1 auStack_30 [20];
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  FUN_004d9b4a();
  puVar1 = DAT_004da6cc;
  FUN_0043c0e4(DAT_004da6cc,0x3758,0);
  uVar2 = DAT_004da6d0;
  FUN_0043c0e4(DAT_004da6d0,0x38ec,0);
  *puVar1 = 2;
  puVar1[1] = 0;
  *(undefined2 *)(puVar1 + 2) = 0xd;
  *(undefined2 *)(puVar1 + 4) = 3;
  puVar1[8] = 7;
  *(undefined4 *)(puVar1 + 0x18) = param_1;
  FUN_004d9ba6();
  FUN_004905f4(auStack_30,uVar2,0x38ec);
  FUN_00439c04(auStack_44,auStack_30,0x14);
  iVar3 = FUN_00490c32(auStack_44,DAT_004da7c8,puVar1);
  if (iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar3 = DAT_004da7d8;
      if (local_34 != 0) {
        iVar3 = local_34;
      }
      FUN_0043d574(1,DAT_004da600,DAT_004da5fc,DAT_004da7f0,0x116,DAT_004da7dc,iVar3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      iVar3 = DAT_004da7d8;
      if (local_34 != 0) {
        iVar3 = local_34;
      }
      compress_log_output(0x4400000,DAT_004da7e4,DAT_004da7e4,iVar3);
    }
    iVar3 = -3;
  }
  else {
    iVar3 = Thread_MsgPbNotifyByBle(1,0xe0,uVar2,local_38 & 0xffff);
    if (iVar3 == 0) {
      iVar3 = 0;
    }
  }
  return iVar3;
}

