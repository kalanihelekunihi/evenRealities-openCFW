
undefined8 FUN_0054e1a8(uint param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  
  puVar1 = DAT_0054e5d8;
  if (*DAT_0054e624 == '\0') {
    if (param_1 == 0) {
      if ((int)*DAT_0054e5d8 < 1) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0xecc;
          param_2 = DAT_0054ed50;
          FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_inject_event_0054e658);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0054ed54,DAT_0054ed54);
        }
        FUN_0054dfb4(1);
      }
      else {
        FUN_0054daf4();
        *puVar1 = *puVar1 - 1;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0xec8;
          param_2 = DAT_0054ed48;
          FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_inject_event_0054e658,0xec8,
                       DAT_0054ed48,*puVar1,*(undefined4 *)(DAT_0054ed38 + *puVar1 * 4));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          param_1 = *(uint *)(DAT_0054ed38 + *puVar1 * 4);
          compress_log_output(0x10800000,DAT_0054ed4c,DAT_0054ed4c,*puVar1);
        }
        FUN_0054db30();
        FUN_0054dc24();
      }
    }
    else if (param_1 == 2) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0xec0;
        param_2 = DAT_0054ed3c;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_inject_event_0054e658,0xec0,DAT_0054ed3c
                     ,*(undefined4 *)(DAT_0054ed38 + *DAT_0054e5d8 * 4),*DAT_0054e5d8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        param_1 = *DAT_0054e5d8;
        compress_log_output(0x10800000,DAT_0054ed40,DAT_0054ed40,
                            *(undefined4 *)(DAT_0054ed38 + *DAT_0054e5d8 * 4));
      }
      *DAT_0054ed44 = (char)*DAT_0054e5d8 + '\x01';
    }
    else if (param_1 < 2) {
      if ((int)*DAT_0054e5d8 < 1) {
        FUN_0054daf4();
        *puVar1 = *puVar1 + 1;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0xed5;
          param_2 = DAT_0054ed58;
          FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_inject_event_0054e658,0xed5,
                       DAT_0054ed58,*puVar1,*(undefined4 *)(DAT_0054ed38 + *puVar1 * 4));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          param_1 = *(uint *)(DAT_0054ed38 + *puVar1 * 4);
          compress_log_output(0x10800000,DAT_0054ed5c,DAT_0054ed5c,*puVar1);
        }
        FUN_0054db30();
        FUN_0054dc24();
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0xed9;
          param_2 = DAT_0054ed60;
          FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_inject_event_0054e658);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0054ed64,DAT_0054ed64);
        }
        FUN_0054dfb4(0);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0xede;
        param_2 = DAT_0054ed68;
        FUN_0043d574(2,DAT_0054e448,DAT_0054e444,PTR_s_mode_inject_event_0054e658);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__navigation_ui_Mode_inject_event_0054ed6c,
                            PTR_s__navigation_ui_Mode_inject_event_0054ed6c);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0xeb6;
      param_2 = PTR_s_Mode_is_animating__ignore_event_0054e654;
      FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_inject_event_0054e658,0xeb6,
                   PTR_s_Mode_is_animating__ignore_event_0054e654,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_is_animating_0054e65c,
                          PTR_s__navigation_ui_Mode_is_animating_0054e65c);
    }
  }
  return CONCAT44(param_2,param_1);
}

