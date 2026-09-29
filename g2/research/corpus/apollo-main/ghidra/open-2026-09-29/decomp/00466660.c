
undefined4 FUN_00466660(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_004667ec;
  FUN_0043c0e4(DAT_004667ec,0x2c,0);
  iVar1 = DAT_004667f0;
  FUN_00439be4(iVar2,*(undefined4 *)(DAT_004667f0 + 0x14),0x14);
  FUN_00439be4(iVar2 + 0x14,*(undefined4 *)(iVar1 + 0xc),0xc);
  FUN_00439be4(iVar2 + 0x20,*(undefined4 *)(iVar1 + 0x10),0xc);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_00466864,0x143,DAT_00466860);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_004666ca:
    compress_log_output(0xc000000,DAT_00466868,DAT_00466868);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_004666ca;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_00466864,0x14a,DAT_0046686c,
                 *(undefined1 *)(iVar2 + 1),*(undefined1 *)(iVar2 + 2),*(undefined1 *)(iVar2 + 3),
                 *(undefined4 *)(iVar2 + 0x18),*(undefined4 *)(iVar2 + 0x24),
                 *(undefined1 *)(iVar2 + 0xb));
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0046671c:
    compress_log_output(0xd800000,DAT_00466870,DAT_00466870,*(undefined1 *)(iVar2 + 1),
                        *(undefined1 *)(iVar2 + 2),*(undefined1 *)(iVar2 + 3),
                        *(undefined4 *)(iVar2 + 0x18),*(undefined4 *)(iVar2 + 0x24),
                        *(undefined1 *)(iVar2 + 0xb));
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0046671c;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_00466864,0x151,DAT_0046682c,
                 *(undefined1 *)(iVar2 + 0x11),*(undefined1 *)(iVar2 + 0x10),
                 *(undefined1 *)(iVar2 + 0xf),*(undefined1 *)(iVar2 + 0xe),
                 *(undefined1 *)(iVar2 + 0xd),*(undefined1 *)(iVar2 + 0xc));
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00466784:
    compress_log_output(0xd800000,PTR_s__srv_universal_setting_ring_mac__00466830,
                        PTR_s__srv_universal_setting_ring_mac__00466830,
                        *(undefined1 *)(iVar2 + 0x11),*(undefined1 *)(iVar2 + 0x10),
                        *(undefined1 *)(iVar2 + 0xf),*(undefined1 *)(iVar2 + 0xe),
                        *(undefined1 *)(iVar2 + 0xd),*(undefined1 *)(iVar2 + 0xc));
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00466784;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_00466864,0x159,DAT_00466874);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004667e0;
  }
  compress_log_output(0xc000000,DAT_00466878,DAT_00466878);
LAB_004667e0:
  FUN_004661a6();
  return 0;
}

