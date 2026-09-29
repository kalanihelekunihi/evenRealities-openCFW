
void FUN_00494484(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                   PTR_s_evenhub_unbind_event_container_00494b7c,0x29f,
                   PTR_s_evenhub_unbind_event_container__m_00494b78);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__evenhub_ui_evenhub_unbind_event_00494b88,
                          PTR_s__evenhub_ui_evenhub_unbind_event_00494b88);
    }
  }
  else if (*(char *)(param_1 + 0x34) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                   PTR_s_evenhub_unbind_event_container_00494b7c,0x2a4,
                   PTR_s_evenhub_unbind_event_container__n_00494b8c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_unbind_event_00494b90);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                   PTR_s_evenhub_unbind_event_container_00494b7c,0x2ab,
                   PTR_s_evenhub_unbind_event_container__u_00494b94,*(undefined4 *)(param_1 + 0x1c),
                   param_1 + 0x20,*(undefined1 *)(param_1 + 0x30));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xcc00000,PTR_s__evenhub_ui_evenhub_unbind_event_00494b98,
                          PTR_s__evenhub_ui_evenhub_unbind_event_00494b98,
                          *(undefined4 *)(param_1 + 0x1c),param_1 + 0x20,
                          *(undefined1 *)(param_1 + 0x30));
    }
    FUN_0043c0e4(param_1 + 0x10,0x24,0);
    *(undefined1 *)(param_1 + 0x34) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                   PTR_s_evenhub_unbind_event_container_00494b7c,0x2b1,
                   PTR_s_evenhub_unbind_event_container__u_00494b9c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_unbind_event_00494ba0,
                          PTR_s__evenhub_ui_evenhub_unbind_event_00494ba0);
    }
  }
  return;
}

