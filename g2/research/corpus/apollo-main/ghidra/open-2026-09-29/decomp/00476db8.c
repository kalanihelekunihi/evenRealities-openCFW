
undefined4 _isConnParamsFast(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477764,0xc6,DAT_00477760,
                 *(undefined2 *)(param_1 + 0x18),*(undefined2 *)(param_1 + 0x18),
                 *(undefined2 *)(param_1 + 0x1a),*(undefined2 *)(DAT_0047775c + 4),
                 *(undefined2 *)(DAT_0047775c + 6),*(undefined2 *)(DAT_0047775c + 8));
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00476e0e:
    compress_log_output(0x11800000,DAT_00477768,DAT_00477768,*(undefined2 *)(param_1 + 0x18),
                        *(undefined2 *)(param_1 + 0x18),*(undefined2 *)(param_1 + 0x1a),
                        *(undefined2 *)(DAT_0047775c + 4),*(undefined2 *)(DAT_0047775c + 6),
                        *(undefined2 *)(DAT_0047775c + 8));
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00476e0e;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477764,0xc9,DAT_0047776c,
                 ((uint)*(ushort *)(param_1 + 0x18) * 0x4e2) / 1000,0x18);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00476e80:
    compress_log_output(0x10800000,DAT_00477770,DAT_00477770,
                        ((uint)*(ushort *)(param_1 + 0x18) * 0x4e2) / 1000,0x18);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00476e80;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477764,0xca,DAT_00477a6c,
                 *(undefined2 *)(param_1 + 0x1a));
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00476eea;
  }
  compress_log_output(0x10400000,DAT_00477a70,DAT_00477a70,*(undefined2 *)(param_1 + 0x1a));
LAB_00476eea:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477764,0xcb,DAT_00477a74,
                 ((uint)*(ushort *)(param_1 + 0x1c) * 10000) / 1000);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00477a78,DAT_00477a78,
                        ((uint)*(ushort *)(param_1 + 0x1c) * 10000) / 1000);
  }
  if (*(ushort *)(param_1 + 0x18) < 0x19) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477764,0xce,DAT_00477a7c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00477a80,DAT_00477a80);
    }
    uVar2 = 0xa3;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477764,0xd1,DAT_00477a84);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00477a88,DAT_00477a88);
    }
    uVar2 = 0xa4;
  }
  return uVar2;
}

