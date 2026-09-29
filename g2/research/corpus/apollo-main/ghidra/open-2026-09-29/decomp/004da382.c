
undefined4 FUN_004da382(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

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
  *puVar1 = 0xb;
  puVar1[1] = 0;
  *(undefined2 *)(puVar1 + 2) = 0x10;
  *(undefined4 *)(puVar1 + 4) = param_1;
  FUN_0044b5a0(puVar1 + 8,param_2,0x10);
  *(int *)(puVar1 + 0x18) = param_3;
  *(undefined4 *)(puVar1 + 0x1c) = param_4;
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
      FUN_0043d574(1,DAT_004da600,DAT_004da5fc,DAT_004da808,0x17c,DAT_004da7dc,iVar2);
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
    iVar2 = FUN_0045a570();
    if (iVar2 == 1) {
      if (param_3 == 0x4c) {
        FUN_0045aaca(0xe0,uVar3,local_40 & 0xffff,300);
      }
      else {
        FUN_00464bb2(0xe0,uVar3,local_40 & 0xffff,0);
      }
    }
    uVar3 = 0;
  }
  return uVar3;
}

