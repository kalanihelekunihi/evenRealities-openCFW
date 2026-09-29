
void FUN_004661a6(void)

{
  int iVar1;
  int iVar2;
  undefined1 local_3c [2];
  undefined1 auStack_3a [22];
  undefined1 auStack_24 [12];
  undefined1 auStack_18 [12];
  
  FUN_0043c0e4(local_3c,0x30,0);
  iVar2 = FUN_0045a568();
  iVar1 = DAT_004667ec;
  local_3c[0] = iVar2 != 1;
  FUN_00439be4(auStack_3a,DAT_004667ec,0x14);
  FUN_00439be4(auStack_24,iVar1 + 0x14,0xc);
  FUN_00439be4(auStack_18,iVar1 + 0x20,0xc);
  FUN_00465480(0x10d,local_3c,0x30,0,5);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00466800,DAT_004667fc,DAT_0046681c,0x8b,DAT_00466818,local_3c[0],
                 *(undefined1 *)(iVar1 + 1),*(undefined1 *)(iVar1 + 2),*(undefined1 *)(iVar1 + 3),
                 *(undefined1 *)(iVar1 + 4),*(undefined4 *)(iVar1 + 0x18),
                 *(undefined1 *)(iVar1 + 0xb));
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x11c00000,DAT_00466820,DAT_00466820,local_3c[0],*(undefined1 *)(iVar1 + 1),
                        *(undefined1 *)(iVar1 + 2),*(undefined1 *)(iVar1 + 3),
                        *(undefined1 *)(iVar1 + 4),*(undefined4 *)(iVar1 + 0x18),
                        *(undefined1 *)(iVar1 + 0xb));
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00466800,DAT_004667fc,DAT_0046681c,0x92,DAT_00466824,
                 *(undefined1 *)(iVar1 + 5),*(undefined1 *)(iVar1 + 6),*(undefined1 *)(iVar1 + 7),
                 *(undefined1 *)(iVar1 + 8),*(undefined1 *)(iVar1 + 9),*(undefined1 *)(iVar1 + 10));
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x11800000,DAT_00466828,DAT_00466828,*(undefined1 *)(iVar1 + 5),
                        *(undefined1 *)(iVar1 + 6),*(undefined1 *)(iVar1 + 7),
                        *(undefined1 *)(iVar1 + 8),*(undefined1 *)(iVar1 + 9),
                        *(undefined1 *)(iVar1 + 10));
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00466800,DAT_004667fc,DAT_0046681c,0x99,DAT_0046682c,
                 *(undefined1 *)(iVar1 + 0x11),*(undefined1 *)(iVar1 + 0x10),
                 *(undefined1 *)(iVar1 + 0xf),*(undefined1 *)(iVar1 + 0xe),
                 *(undefined1 *)(iVar1 + 0xd),*(undefined1 *)(iVar1 + 0xc));
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x11800000,PTR_s__srv_universal_setting_ring_mac__00466830,
                        PTR_s__srv_universal_setting_ring_mac__00466830,
                        *(undefined1 *)(iVar1 + 0x11),*(undefined1 *)(iVar1 + 0x10),
                        *(undefined1 *)(iVar1 + 0xf),*(undefined1 *)(iVar1 + 0xe),
                        *(undefined1 *)(iVar1 + 0xd),*(undefined1 *)(iVar1 + 0xc));
  }
  return;
}

