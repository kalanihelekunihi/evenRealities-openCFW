
undefined4 _kvdbUpdataTime(void)

{
  int iVar1;
  byte local_10 [10];
  short local_6;
  
  iVar1 = SVC_KvdbBlobRead(DAT_0058580c,local_10,0xc);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0058581c,DAT_00585818,DAT_00585814,0x2d,DAT_00585810,local_10[0],3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00585820,DAT_00585820,local_10[0],3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0058581c,DAT_00585818,DAT_00585814,0x2e,DAT_00585824,local_6,
                   *(undefined2 *)(DAT_00585808 + 10));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00585828,DAT_00585828,local_6,
                          *(undefined2 *)(DAT_00585808 + 10));
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0058581c,DAT_00585818,DAT_00585814,0x2f,DAT_0058582c,
                   (int)*(char *)(DAT_00585808 + 8),*(undefined4 *)(DAT_00585808 + 4));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00585830,DAT_00585830,(int)*(char *)(DAT_00585808 + 8),
                          *(undefined4 *)(DAT_00585808 + 4));
    }
    if ((local_6 != *(short *)(DAT_00585808 + 10)) && (local_10[0] < 3)) {
      SVC_KvdbWriteTime(*(undefined4 *)(DAT_00585808 + 4),(int)*(char *)(DAT_00585808 + 8));
    }
    return 0;
  }
  SVC_KvdbWriteTime(*(undefined4 *)(DAT_00585808 + 4),(int)*(char *)(DAT_00585808 + 8));
  return 0;
}

