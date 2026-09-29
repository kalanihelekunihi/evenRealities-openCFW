
undefined4 FUN_004f6664(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = DAT_004f6d6c;
  iVar1 = 0;
  while( true ) {
    if ((int)(uint)*(ushort *)(DAT_004f6d6c + 0x280) <= iVar1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f6e60,0x558,DAT_004f6e68,param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004f6fac,DAT_004f6fac,param_1);
      }
      return 0xffffffff;
    }
    if (*(int *)(DAT_004f6d6c + iVar1 * 0x10) == param_1) break;
    iVar1 = iVar1 + 1;
  }
  for (; iVar1 < (int)(*(ushort *)(iVar2 + 0x280) - 1); iVar1 = iVar1 + 1) {
    uVar3 = 0;
    do {
      *(undefined1 *)(iVar1 * 0x10 + iVar2 + uVar3) =
           *(undefined1 *)(iVar1 * 0x10 + iVar2 + uVar3 + 0x10);
      uVar3 = uVar3 + 1;
    } while (uVar3 < 0x10);
  }
  *(short *)(iVar2 + 0x280) = *(short *)(iVar2 + 0x280) + -1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f6e60,0x554,DAT_004f6e5c,param_1,
                 *(undefined2 *)(iVar2 + 0x280),param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_004f6e64,DAT_004f6e64,param_1,*(undefined2 *)(iVar2 + 0x280))
    ;
  }
  return 0;
}

