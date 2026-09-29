
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004ac19c(undefined1 param_1,undefined4 param_2,undefined *param_3)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = _DAT_004acb20;
  if ((*_DAT_004acb20 == '\0') && (*_DAT_004acb24 == '\0')) {
    iVar2 = APP_MasterTryReconnectRingByScene(param_1);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x11f;
        param_3 = PTR_s__Box__Scene__d__reconnect_reject_004acb34;
        FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,
                     PTR_s__BoxDetect_TryReconnectRing_004acb2c,0x11f,
                     PTR_s__Box__Scene__d__reconnect_reject_004acb34,param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,_DAT_004acd48,_DAT_004acd48,param_1);
      }
    }
    else {
      *pcVar1 = '\x01';
      if (*_DAT_004acb08 != 0) {
        osTimerStart(*_DAT_004acb08,60000);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x11d;
        param_3 = PTR_s__Box__Scene__d__reconnect_queued_004acb28;
        FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,
                     PTR_s__BoxDetect_TryReconnectRing_004acb2c,0x11d,
                     PTR_s__Box__Scene__d__reconnect_queued_004acb28,param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__box_detect__Box__Scene__d__reco_004acb30,
                            PTR_s__box_detect__Box__Scene__d__reco_004acb30,param_1);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

