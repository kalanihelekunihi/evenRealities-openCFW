
undefined4 FUN_00495f9a(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  iVar2 = param_4;
  iVar1 = FUN_0045a570();
  if (iVar1 == 2) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004964e8,DAT_004961a0,DAT_004964e4,0x527,DAT_004964e0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004964ec,DAT_004964ec);
    }
    uVar3 = 0;
  }
  else if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004964e8,DAT_004961a0,DAT_004964e4,0x52d,DAT_004964f0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004964f4,DAT_004964f4);
    }
    uVar3 = 0xffffffff;
  }
  else if (*(char *)(param_1 + 0x57c) == '\x01') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004964e8,DAT_004961a0,DAT_004964e4,0x532,DAT_004964f8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004964fc,DAT_004964fc);
    }
    uVar3 = 0;
  }
  else if (param_4 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004964e8,DAT_004961a0,DAT_004964e4,0x538,DAT_00496500);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00496504,DAT_00496504);
    }
    uVar3 = 0xffffffff;
  }
  else if (((param_2 == 0x44) || (param_2 == 0x45)) || (param_2 == 10)) {
    uVar4 = **(uint **)(param_3 + 0x10) | (*(uint **)(param_3 + 0x10))[1] << 0x10;
    FUN_004da382(*(undefined4 *)(param_4 + 0x1c),param_4 + 0x20,param_2,uVar4);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004964e8,DAT_004961a0,DAT_004964e4,0x547,DAT_00496510,param_2,uVar4,iVar2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00496514,DAT_00496514,param_2,uVar4);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004964e8,DAT_004961a0,DAT_004964e4,0x53d,DAT_00496508,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0049650c,DAT_0049650c,param_2);
    }
    uVar3 = 1;
  }
  return uVar3;
}

