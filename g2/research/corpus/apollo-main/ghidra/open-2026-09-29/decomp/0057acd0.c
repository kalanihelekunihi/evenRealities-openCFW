
undefined4 SVC_PcmAppUnregister(int param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_0057b3b4;
  if (*(int *)((param_2 & 0xff) * 0xc + DAT_0057b3b4 + 8) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0057b388,DAT_0057b384,DAT_0057b3cc,0xd8,DAT_0057b3c8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0057b3d0);
    }
    uVar2 = 0;
  }
  else if (*(int *)(DAT_0057b3b4 + (param_2 & 0xff) * 0xc) == param_1) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0057b388,DAT_0057b384,DAT_0057b3cc,0xe1,DAT_0057b3dc,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0057b3e0,DAT_0057b3e0,param_1);
    }
    FUN_0043c0e4((param_2 & 0xff) * 0xc + iVar1,0xc,0);
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0057b388,DAT_0057b384,DAT_0057b3cc,0xdd,DAT_0057b3d4,param_1,
                   *(undefined4 *)(iVar1 + (param_2 & 0xff) * 0xc));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_0057b3d8,DAT_0057b3d8,param_1,
                          *(undefined4 *)(iVar1 + (param_2 & 0xff) * 0xc));
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

