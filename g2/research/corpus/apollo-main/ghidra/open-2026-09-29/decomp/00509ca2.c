
undefined4 ui_common_api_fn_00509ca2(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  ushort uVar3;
  uint uVar4;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00509fa4,DAT_00509fa0,DAT_00509fb0,0x3f,DAT_00509fac,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00509fb4,DAT_00509fb4);
    }
    uVar2 = 0xfffffffc;
  }
  else if ((param_2 == 0) || ((param_3 & 0xffff) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00509fa4,DAT_00509fa0,DAT_00509fb0,0x44,DAT_00509fb8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00509fbc,DAT_00509fbc);
    }
    uVar2 = 0xfffffffd;
  }
  else {
    uVar4 = 0x200 - *(ushort *)(param_1 + 0x204);
    if ((uVar4 & 0xffff) < (param_3 & 0xffff)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00509fa4,DAT_00509fa0,DAT_00509fb0,0x4b,DAT_00509fc0,uVar4 & 0xffff,
                     param_3 & 0xffff);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_00509fc4,DAT_00509fc4,uVar4 & 0xffff,param_3 & 0xffff);
      }
      uVar2 = 0xffffffff;
    }
    else {
      for (uVar3 = 0; (uint)uVar3 < (param_3 & 0xffff); uVar3 = uVar3 + 1) {
        *(undefined1 *)(param_1 + (uint)*(ushort *)(param_1 + 0x200)) =
             *(undefined1 *)(param_2 + (uint)uVar3);
        uVar4 = *(ushort *)(param_1 + 0x200) + 1;
        *(short *)(param_1 + 0x200) = (short)uVar4 + (short)(uVar4 / 0x200) * -0x200;
        *(short *)(param_1 + 0x204) = *(short *)(param_1 + 0x204) + 1;
      }
      uVar2 = 0;
    }
  }
  return uVar2;
}

