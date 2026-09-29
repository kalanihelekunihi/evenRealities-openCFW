
undefined4 FUN_004d9c86(undefined1 param_1,undefined1 param_2,ushort param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_50;
  undefined4 local_4c;
  uint local_48;
  uint local_44;
  undefined1 auStack_3c [20];
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  FUN_004d9b4a();
  puVar2 = DAT_004da6cc;
  FUN_0043c0e4(DAT_004da6cc,0x3758,0);
  uVar3 = DAT_004da6d0;
  FUN_0043c0e4(DAT_004da6d0,0x38ec,0);
  *puVar2 = param_1;
  puVar2[1] = param_2;
  *(ushort *)(puVar2 + 2) = param_3;
  uVar1 = (undefined1)param_4;
  if (param_3 == 4) {
    puVar2[4] = uVar1;
  }
  else if (param_3 == 8) {
    puVar2[4] = uVar1;
  }
  else if (param_3 == 10) {
    puVar2[4] = uVar1;
  }
  else if (param_3 == 0xc) {
    puVar2[4] = uVar1;
  }
  else {
    if (param_3 != 0xf) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_48 = (uint)param_3;
        local_4c = DAT_004da7cc;
        local_50 = 0x94;
        FUN_0043d574(1,DAT_004da600,DAT_004da5fc,DAT_004da7d0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004da7d4,DAT_004da7d4,param_3);
      }
      FUN_004d9ba6();
      return 0xffffffff;
    }
    puVar2[8] = uVar1;
  }
  FUN_004d9ba6();
  FUN_004905f4(auStack_3c,uVar3,0x38ec);
  FUN_00439c04(&local_50,auStack_3c,0x14);
  iVar4 = FUN_00490c32(&local_50,DAT_004da7c8,puVar2);
  if (iVar4 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,0xe0,uVar3,local_44 & 0xffff);
  }
  return uVar3;
}

