
undefined8 ui_common_api_fn_00509e14(int param_1,int param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  ushort uVar3;
  uint uVar4;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x73;
      FUN_0043d574(2,DAT_00509fa4,DAT_00509fa0,DAT_00509fc8,0x73,DAT_00509fac);
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
      param_3 = 0x78;
      FUN_0043d574(2,DAT_00509fa4,DAT_00509fa0,DAT_00509fc8,0x78,DAT_00509fcc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00509fd0,DAT_00509fd0);
    }
    uVar2 = 0xfffffffd;
  }
  else if (*(short *)(param_1 + 0x204) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x7d;
      FUN_0043d574(2,DAT_00509fa4,DAT_00509fa0,DAT_00509fc8,0x7d,DAT_00509fd4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00509fd8,DAT_00509fd8);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = param_3;
    if ((uint)*(ushort *)(param_1 + 0x204) <= (param_3 & 0xffff)) {
      uVar2 = (uint)*(ushort *)(param_1 + 0x204);
    }
    for (uVar3 = 0; (uint)uVar3 < (uVar2 & 0xffff); uVar3 = uVar3 + 1) {
      *(undefined1 *)(param_2 + (uint)uVar3) =
           *(undefined1 *)(param_1 + (uint)*(ushort *)(param_1 + 0x202));
      uVar4 = *(ushort *)(param_1 + 0x202) + 1;
      *(short *)(param_1 + 0x202) = (short)uVar4 + (short)(uVar4 / 0x200) * -0x200;
      *(short *)(param_1 + 0x204) = *(short *)(param_1 + 0x204) + -1;
    }
    uVar2 = uVar2 & 0xffff;
  }
  return CONCAT44(param_3,uVar2);
}

