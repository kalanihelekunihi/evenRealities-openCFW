
undefined8 FUN_00500b7c(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = 0x11f;
    param_2 = PTR_s_STEP3__send_OS_NOTIFY_PB_FILE_TR_005011c4;
    param_3 = param_1;
    FUN_0043d574(3,DAT_00501188,DAT_00501184,PTR_s_handle_notify_pb_file_transmit_s_005011c8,0x11f,
                 PTR_s_STEP3__send_OS_NOTIFY_PB_FILE_TR_005011c4,param_1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__dashboard_ext_STEP3__send_OS_NO_005011cc,
                        PTR_s__dashboard_ext_STEP3__send_OS_NO_005011cc,param_1,uVar3,param_2,
                        param_3);
  }
  puVar1 = DAT_00501170;
  FUN_0043c0e4(DAT_00501170,0x1024,0);
  *puVar1 = 4;
  *(undefined4 *)(puVar1 + 4) = param_1;
  *(undefined2 *)(puVar1 + 8) = 7;
  *(undefined4 *)(puVar1 + 0xc) = 1;
  FUN_00500a0c();
  return CONCAT44(param_2,uVar3);
}

