
undefined4 SVC_PcmAppRegister(undefined4 param_1,byte param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_0057b3b4;
  if ((param_2 < 2) && (param_3 != 0)) {
    if (*(int *)((uint)param_2 * 0xc + DAT_0057b3b4 + 8) != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0057b388,DAT_0057b384,DAT_0057b3ac,0xc6,DAT_0057b3b8,
                     *(undefined4 *)(iVar1 + (uint)param_2 * 0xc));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0057b3bc,DAT_0057b3bc,
                            *(undefined4 *)(iVar1 + (uint)param_2 * 0xc));
      }
      FUN_0043c0e4(iVar1 + (uint)param_2 * 0xc,0xc,0);
    }
    *(undefined4 *)(iVar1 + (uint)param_2 * 0xc) = param_1;
    *(byte *)((uint)param_2 * 0xc + iVar1 + 4) = param_2;
    *(int *)(iVar1 + (uint)param_2 * 0xc + 8) = param_3;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0057b388,DAT_0057b384,DAT_0057b3ac,0xd0,DAT_0057b3c0,param_1,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0057b3c4,DAT_0057b3c4,param_1,param_2);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b3ac,0xbf,DAT_0057b3a8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0057b3b0,DAT_0057b3b0);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

