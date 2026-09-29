
undefined4 AUDM_appAcquire(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = FUN_0045a568();
  if (iVar2 != 2) {
    return 0;
  }
  if ((param_1 < 8) && (param_1 != 0)) {
    if (*(char *)(DAT_0054f978 + (uint)param_1) != '\x01') {
      *(undefined1 *)(DAT_0054f978 + (uint)param_1) = 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar1 = AUDM_activeAppCount();
        FUN_0043d574(3,DAT_0054f988,DAT_0054f984,DAT_0054f980,0x35,DAT_0054f998,param_1,uVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar1 = AUDM_activeAppCount();
        compress_log_output(0xc800000,DAT_0054f99c,DAT_0054f99c,param_1,uVar1);
      }
      iVar2 = AUDM_activeAppCount();
      if (iVar2 == 1) {
        service_audio_lc3_encoder_setup(DAT_0054f9a0);
        aud_send_message_type1(1);
        aud_send_message_type0(1);
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0054f988,DAT_0054f984,DAT_0054f980,0x3c,DAT_0054f9a4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0054f9a8,DAT_0054f9a8);
        }
      }
      return 0;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0054f988,DAT_0054f984,DAT_0054f980,0x30,DAT_0054f990,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0054f994,DAT_0054f994,param_1);
    }
    return 0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,DAT_0054f988,DAT_0054f984,DAT_0054f980,0x2b,DAT_0054f97c,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_0054f98c,DAT_0054f98c);
  }
  return 0xffffffff;
}

