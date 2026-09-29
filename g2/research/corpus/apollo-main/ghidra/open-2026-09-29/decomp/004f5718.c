
longlong FUN_004f5718(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  ushort uVar4;
  
  iVar2 = DAT_004f5c3c;
  FUN_0043c0e4(DAT_004f5c3c + 8,0x2e40,0,param_4,param_2,param_3,param_4);
  iVar1 = DAT_004f62f0;
  uVar3 = 0;
  if (*(char *)(DAT_004f62f0 + 0x1220) != '\0') {
    uVar4 = 0;
    while ((uVar4 < 0x14 && (uVar3 < 0x28))) {
      if (*(char *)((uint)uVar4 * 0xe8 + iVar1 + 0xe4) != '\0') {
        FUN_004f55e0(iVar1 + (uint)uVar4 * 0xe8,iVar2 + (uint)uVar3 * 0x128 + 8);
        uVar3 = uVar3 + 1;
      }
      uVar4 = uVar4 + 1;
    }
  }
  *DAT_004f62f4 = 1;
  *DAT_004f62f8 = (uint)uVar3;
  if ((((*(short *)(DAT_004f62fc + 0x280) != 0) && (*DAT_004f5c44 == 1)) && (*DAT_004f6300 != 0)) &&
     (*DAT_004f6304 != 0)) {
    FUN_0043c0e4(DAT_004f62fc,0x288,0);
  }
  if (*(short *)(DAT_004f5c40 + 0x280) != 0) {
    FUN_004f6328();
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x2a9;
    FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f630c,0x2a9,DAT_004f6308,uVar3);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004f6318,DAT_004f6318,uVar3);
  }
  return (ulonglong)param_2 << 0x20;
}

