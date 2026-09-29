
undefined8
APP_MasterPublishRingLinkReady
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  
  pcVar1 = DAT_004a3120;
  if (*DAT_004a3124 == '\0') {
    if (*DAT_004a3120 == '\x02') {
      if ((*DAT_004a3134 == 0) || (*(char *)(*DAT_004a3134 + 0x55) == '\0')) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0x525;
          param_2 = DAT_004a3138;
          FUN_0043d574(2,DAT_004a28f0,DAT_004a28ec,DAT_004a312c);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004a313c);
        }
      }
      else {
        *DAT_004a3124 = '\x01';
        *DAT_004a3140 = 0;
        *DAT_004a3144 = 1;
        FUN_004b82e8(3);
        iVar2 = central_is_ring_owner_side_004a2914();
        if (iVar2 != 0) {
          RING_ConnectPolicyNotifyConnectSuccessSoon();
        }
        central_emit_ring_link_event_004a153c(3);
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0x531;
          param_2 = DAT_004a3148;
          FUN_0043d574(3,DAT_004a28f0,DAT_004a28ec,DAT_004a312c);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004a314c,DAT_004a314c);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = _ringLinkStateName(*pcVar1);
        param_1 = 0x521;
        param_2 = DAT_004a3128;
        FUN_0043d574(2,DAT_004a28f0,DAT_004a28ec,DAT_004a312c,0x521,DAT_004a3128,uVar3,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar3 = _ringLinkStateName(*pcVar1);
        compress_log_output(0x8400000,DAT_004a3130,DAT_004a3130,uVar3);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

