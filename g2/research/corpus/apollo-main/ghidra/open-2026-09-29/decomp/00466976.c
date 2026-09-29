
undefined4 FUN_00466976(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                   PTR_s_setting_data_recv_handler_00467304,0x7d,PTR_s_pMessage_is_NULL_00467300,
                   param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_pMessage_is_NULL_004674ac,
                          PTR_s__setting_pMessage_is_NULL_004674ac);
    }
    uVar2 = 1;
  }
  else {
    if (*(short *)(param_1 + 8) == 3) {
      FUN_00466abc();
      iVar1 = setting_respond_to_app_serialize();
      if (iVar1 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                       PTR_s_setting_data_recv_handler_00467304,0x88,
                       PTR_s_setting_respond_to_app_serialize_004674b0,iVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__setting_setting_respond_to_app_s_004674b4,
                              PTR_s__setting_setting_respond_to_app_s_004674b4,iVar1);
        }
      }
    }
    else if (*(short *)(param_1 + 8) == 4) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                     PTR_s_setting_data_recv_handler_00467304,0x8b,
                     PTR_s_Processing_APP_request_004674b8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__setting_Processing_APP_request_004674bc,
                            PTR_s__setting_Processing_APP_request_004674bc);
      }
      iVar1 = setting_respond_with_local_data_serialize();
      if (iVar1 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                       PTR_s_setting_data_recv_handler_00467304,0x90,
                       PTR_s_setting_respond_with_local_data_s_004674c0,iVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__setting_setting_respond_with_lo_004674c4,
                              PTR_s__setting_setting_respond_with_lo_004674c4,iVar1);
        }
      }
    }
    uVar2 = 0;
  }
  return uVar2;
}

