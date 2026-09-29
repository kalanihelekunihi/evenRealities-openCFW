
undefined4 SVC_Settings_SaveAlsScaleToKV(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  
  iVar1 = DAT_0046c6a8;
  if (*(char *)(DAT_0046c6a8 + 0x2c) != '\0') {
    SVC_KvdbWriteAlsScale(DAT_0046c6a8 + 0x20);
    *(undefined1 *)(iVar1 + 0x2c) = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c6bc,0x170,DAT_0046c6b8,
                   *(undefined4 *)(iVar1 + 0x24),in_r3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0046c6c0,DAT_0046c6c0,*(undefined4 *)(iVar1 + 0x24));
    }
  }
  return 0;
}

