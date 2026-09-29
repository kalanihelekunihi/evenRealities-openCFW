
int FUN_00494610(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_evenhub_ui_00494b84,DAT_00494b80,DAT_00494ba8,699,DAT_00494ba4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00494bac,DAT_00494bac);
    }
    iVar1 = -1;
  }
  else if (*(char *)(param_1 + 0x34) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_evenhub_ui_00494b84,DAT_00494b80,DAT_00494ba8,0x2c1,DAT_00494bb0,param_2)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00494bb4,DAT_00494bb4,param_2);
    }
    iVar1 = -1;
  }
  else if (*(int *)(param_1 + 0x14) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_evenhub_ui_00494b84,DAT_00494b80,DAT_00494ba8,0x2c7,DAT_00494bb8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00494bbc,DAT_00494bbc);
    }
    iVar1 = -1;
  }
  else if (*(int *)(param_1 + 0x10) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_evenhub_ui_00494b84,DAT_00494b80,DAT_00494ba8,0x2cd,DAT_00494bc0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00494bc4,DAT_00494bc4);
    }
    iVar1 = -1;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_evenhub_ui_00494b84,DAT_00494b80,DAT_00494ba8,0x2d5,DAT_00494bc8,param_2,
                   *(undefined4 *)(param_1 + 0x1c),param_1 + 0x20,*(undefined1 *)(param_1 + 0x30));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_00494bcc,DAT_00494bcc,param_2,
                          *(undefined4 *)(param_1 + 0x1c),param_1 + 0x20,
                          *(undefined1 *)(param_1 + 0x30));
    }
    iVar1 = (**(code **)(param_1 + 0x14))
                      (*(undefined4 *)(param_1 + 0x10),param_2,param_3,
                       *(undefined4 *)(param_1 + 0x18));
    if (iVar1 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_evenhub_ui_00494b84,DAT_00494b80,DAT_00494ba8,0x2e0,DAT_00494bd0,iVar1)
        ;
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__evenhub_ui_evenhub_inject_event_00494bd4,
                            PTR_s__evenhub_ui_evenhub_inject_event_00494bd4,iVar1);
      }
    }
  }
  return iVar1;
}

