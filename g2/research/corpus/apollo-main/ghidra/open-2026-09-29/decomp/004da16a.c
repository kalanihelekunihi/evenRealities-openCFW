
undefined4
FUN_004da16a(byte param_1,undefined4 param_2,undefined4 param_3,char param_4,undefined4 param_5,
            short param_6)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_4c [12];
  uint local_40;
  int local_3c;
  undefined1 auStack_38 [20];
  
  FUN_004d9b4a();
  puVar1 = DAT_004da6cc;
  FUN_0043c0e4(DAT_004da6cc,0x3758,0);
  uVar3 = DAT_004da6d0;
  FUN_0043c0e4(DAT_004da6d0,0x38ec,0);
  *puVar1 = 2;
  puVar1[1] = 0;
  *(undefined2 *)(puVar1 + 2) = 0xd;
  if (param_1 == 0) {
    *(undefined2 *)(puVar1 + 4) = 3;
    puVar1[8] = param_4;
    if ((param_4 == '\0') || (param_4 == '\x03')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004da600,DAT_004da5fc,DAT_004da7f8,0x134,DAT_004da7f4,param_6);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004da7fc,DAT_004da7fc,param_6);
      }
      if (param_6 == 0) {
        puVar1[9] = 3;
      }
      else if (param_6 == 1) {
        puVar1[9] = 1;
      }
      else if (param_6 == 4) {
        puVar1[9] = 2;
      }
    }
    if (param_4 == '\a') {
      *(undefined4 *)(puVar1 + 0x18) = 0;
    }
  }
  else if (param_1 == 2) {
    *(undefined2 *)(puVar1 + 4) = 2;
    *(undefined4 *)(puVar1 + 8) = param_2;
    FUN_0044b5a0(puVar1 + 0xc,param_3,0x10);
    puVar1[0x1c] = param_4;
  }
  else {
    if (1 < param_1) {
      FUN_004d9ba6();
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004da600,DAT_004da5fc,DAT_004da7f8,0x153,DAT_004da800,param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004da804,DAT_004da804,param_1);
      }
      return 0xffffffff;
    }
    *(undefined2 *)(puVar1 + 4) = 1;
    *(undefined4 *)(puVar1 + 8) = param_2;
    FUN_0044b5a0(puVar1 + 0xc,param_3,0x10);
    puVar1[0x60] = param_4;
    *(undefined4 *)(puVar1 + 0x5c) = param_5;
  }
  FUN_004d9ba6();
  FUN_004905f4(auStack_38,uVar3,0x38ec);
  FUN_00439c04(auStack_4c,auStack_38,0x14);
  iVar2 = FUN_00490c32(auStack_4c,DAT_004da7c8,puVar1);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar2 = DAT_004da7d8;
      if (local_3c != 0) {
        iVar2 = local_3c;
      }
      FUN_0043d574(1,DAT_004da600,DAT_004da5fc,DAT_004da7f8,0x15a,DAT_004da7dc,iVar2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      iVar2 = DAT_004da7d8;
      if (local_3c != 0) {
        iVar2 = local_3c;
      }
      compress_log_output(0x4400000,DAT_004da7e4,DAT_004da7e4,iVar2);
    }
    uVar3 = 0xfffffffd;
  }
  else {
    uVar3 = Thread_MsgPbNotifyByBle(1,0xe0,uVar3,local_40 & 0xffff);
  }
  return uVar3;
}

