
undefined4 FUN_004acb40(int param_1,byte *param_2,uint param_3)

{
  byte bVar1;
  int iVar2;
  
  if (param_1 == 0) {
    APP_PbRxGlassesCaseFrameDataProcess(param_2,param_3 & 0xffff);
  }
  else {
    if (param_1 != 5) {
      return 0xffffffff;
    }
    if ((param_2 == (byte *)0x0) || (param_3 < 8)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004acdc0,DAT_004acdbc,PTR_s_BoxDetect_common_data_handler_004acde0,0x2fc,
                     PTR_s_Invalid_case_sync_data__raw_data_004acddc,param_2,param_3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__box_detect_Invalid_case_sync_da_004acde4,
                            PTR_s__box_detect_Invalid_case_sync_da_004acde4,param_2,param_3);
      }
      return 0xffffffff;
    }
    bVar1 = *param_2;
    if (bVar1 == 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004acdc0,DAT_004acdbc,PTR_s_BoxDetect_common_data_handler_004acde0,0x305,
                     PTR_s_Received_case_sync_request_004acde8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__box_detect_Received_case_sync_r_004acdec,
                            PTR_s__box_detect_Received_case_sync_r_004acdec);
      }
      FUN_004ac828(2);
    }
    else {
      if (bVar1 == 0) {
LAB_004accfa:
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004acdc0,DAT_004acdbc,PTR_s_BoxDetect_common_data_handler_004acde0,
                       0x31c,PTR_s_Unknown_case_sync_message_ID___d_004ace08,*param_2);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__box_detect_Unknown_case_sync_me_004ace0c,
                              PTR_s__box_detect_Unknown_case_sync_me_004ace0c,*param_2);
        }
        return 0xffffffff;
      }
      if (bVar1 == 3) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004acdc0,DAT_004acdbc,PTR_s_BoxDetect_common_data_handler_004acde0,
                       0x311,PTR_s_Received_case_sync_notification_004acdf8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__box_detect_Received_case_sync_n_004acdfc,
                              PTR_s__box_detect_Received_case_sync_n_004acdfc);
        }
        FUN_004ac890(param_2);
      }
      else if (bVar1 < 3) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004acdc0,DAT_004acdbc,PTR_s_BoxDetect_common_data_handler_004acde0,
                       0x30b,PTR_s_Received_case_sync_response_004acdf0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__box_detect_Received_case_sync_r_004acdf4,
                              PTR_s__box_detect_Received_case_sync_r_004acdf4);
        }
        FUN_004ac890(param_2);
      }
      else {
        if (bVar1 != 4) goto LAB_004accfa;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004acdc0,DAT_004acdbc,PTR_s_BoxDetect_common_data_handler_004acde0,
                       0x317,PTR_s_Received_force_out_box_sync___d_004ace00,param_2[7] == 0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__box_detect_Received_force_out_b_004ace04,
                              PTR_s__box_detect_Received_force_out_b_004ace04,param_2[7] == 0);
        }
        FUN_004ac5a2(param_2[7] == 0);
      }
    }
  }
  return 0;
}

