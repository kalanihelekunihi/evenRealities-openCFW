
undefined4
FUN_004942a4(int param_1,int param_2,int param_3,undefined4 param_4,int param_5,undefined1 param_6,
            undefined4 param_7)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00494480,DAT_0049447c,PTR_s_evenhub_bind_event_container_00494b58,0x270,
                   PTR_s_evenhub_bind_event_container__ma_00494b54);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_bind_event_c_00494b5c,
                          PTR_s__evenhub_ui_evenhub_bind_event_c_00494b5c);
    }
    uVar2 = 0xffffffff;
  }
  else if ((param_2 == 0) || (param_3 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00494480,DAT_0049447c,PTR_s_evenhub_bind_event_container_00494b58,0x276,
                   PTR_s_evenhub_bind_event_container__in_00494b60,param_2,param_3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__evenhub_ui_evenhub_bind_event_c_00494b64,
                          PTR_s__evenhub_ui_evenhub_bind_event_c_00494b64,param_2,param_3);
    }
    uVar2 = 0xffffffff;
  }
  else if (*(char *)(param_1 + 0x34) == '\0') {
    *(int *)(param_1 + 0x10) = param_2;
    *(int *)(param_1 + 0x14) = param_3;
    *(undefined4 *)(param_1 + 0x18) = param_7;
    *(undefined4 *)(param_1 + 0x1c) = param_4;
    *(undefined1 *)(param_1 + 0x30) = param_6;
    if (param_5 == 0) {
      *(undefined1 *)(param_1 + 0x20) = 0;
    }
    else {
      FUN_0044b5a0(param_1 + 0x20,param_5,0xf);
      *(undefined1 *)(param_1 + 0x2f) = 0;
    }
    *(undefined1 *)(param_1 + 0x34) = 1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00494480,DAT_0049447c,PTR_s_evenhub_bind_event_container_00494b58,0x295,
                   PTR_s_evenhub_bind_event_container__bo_00494b70,param_4,param_1 + 0x20,param_6);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xcc00000,PTR_s__evenhub_ui_evenhub_bind_event_c_00494b74,
                          PTR_s__evenhub_ui_evenhub_bind_event_c_00494b74,param_4,param_1 + 0x20,
                          param_6);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00494480,DAT_0049447c,PTR_s_evenhub_bind_event_container_00494b58,0x27e,
                   PTR_s_evenhub_bind_event_container__al_00494b68,*(undefined4 *)(param_1 + 0x1c),
                   param_1 + 0x20);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8800000,PTR_s__evenhub_ui_evenhub_bind_event_c_00494b6c,
                          PTR_s__evenhub_ui_evenhub_bind_event_c_00494b6c,
                          *(undefined4 *)(param_1 + 0x1c),param_1 + 0x20);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

