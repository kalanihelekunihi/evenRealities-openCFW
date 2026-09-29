
undefined4 FUN_004f658c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_004f6d6c;
  if (*(ushort *)(DAT_004f6d6c + 0x280) < 0x28) {
    *(undefined4 *)(DAT_004f6d6c + (uint)*(ushort *)(DAT_004f6d6c + 0x280) * 0x10) = param_1;
    iVar3 = (uint)*(ushort *)(iVar1 + 0x280) * 0x10 + iVar1;
    *(undefined4 *)(iVar3 + 8) = param_3;
    *(undefined4 *)(iVar3 + 0xc) = param_4;
    *(short *)(iVar1 + 0x280) = *(short *)(iVar1 + 0x280) + 1;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f6d78,0x542,DAT_004f6d80,param_1,
                   *(undefined2 *)(iVar1 + 0x280));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004f6e58,DAT_004f6e58,param_1,
                          *(undefined2 *)(iVar1 + 0x280));
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004f6d3c,DAT_004f6d38,DAT_004f6d78,0x52e,DAT_004f6d74,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004f6d7c,DAT_004f6d7c,param_1);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

