
undefined8 Thread_MsgEfsNotifyByBle(undefined1 param_1,uint param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = param_2;
  uVar4 = param_4;
  iVar1 = semantic_OtaTransferActive();
  if (iVar1 == 0) {
    uVar2 = Thread_MsgTxByBle(2,1,param_1,param_2 & 0xff,param_3,param_4 & 0xffff,uVar4);
  }
  else {
    iVar1 = FUN_0043d0ce();
    param_3 = uVar3;
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x207;
      FUN_0043d574(4,DAT_00475f98,DAT_00475f94,PTR_s_Thread_MsgEfsNotifyByBle_00475fb8,0x207,
                   PTR_s_OTA_is_going__efs_notify_failed_00475fb4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__ble_msgtx_OTA_is_going__efs_not_00475fbc,
                          PTR_s__ble_msgtx_OTA_is_going__efs_not_00475fbc);
    }
    uVar2 = 8;
  }
  return CONCAT44(param_3,uVar2);
}

