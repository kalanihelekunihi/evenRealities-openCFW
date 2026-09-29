
undefined4 AUDM_appRelease(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = FUN_0045a568();
  if (iVar2 != 2) {
    return 0;
  }
  if ((param_1 < 8) && (param_1 != 0)) {
    if (*(char *)(DAT_0054f978 + (uint)param_1) != '\0') {
      *(undefined1 *)(DAT_0054f978 + (uint)param_1) = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar1 = AUDM_activeAppCount();
        FUN_0043d574(3,DAT_0054f988,DAT_0054f984,DAT_0054f9b0,0x54,DAT_0054f9c0,param_1,uVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar1 = AUDM_activeAppCount();
        compress_log_output(0xc800000,DAT_0054f9c4,DAT_0054f9c4,param_1,uVar1);
      }
      iVar2 = AUDM_activeAppCount();
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0054f988,DAT_0054f984,DAT_0054f9b0,0x58,DAT_0054f9c8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0054f9cc,DAT_0054f9cc);
        }
        aud_send_message_type1(0);
        aud_send_message_type0(0);
      }
      return 0;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0054f988,DAT_0054f984,DAT_0054f9b0,0x4d,DAT_0054f9b8,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0054f9bc,DAT_0054f9bc,param_1);
    }
    return 0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,DAT_0054f988,DAT_0054f984,DAT_0054f9b0,0x48,DAT_0054f9ac,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_0054f9b4,DAT_0054f9b4);
  }
  return 0xffffffff;
}

