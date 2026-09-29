
void FUN_00467308(undefined2 *param_1)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  
  if (param_1 == (undefined2 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                   PTR_s_setting_handle_gesture_control_l_00467e58,0x208,
                   PTR_s_gesture_list_data_is_NULL_00467e54);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_gesture_list_data_is_NU_00467e5c,
                          PTR_s__setting_gesture_list_data_is_NU_00467e5c);
    }
  }
  else {
    bVar1 = (byte)*param_1;
    if (bVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                     PTR_s_setting_handle_gesture_control_l_00467e58,0x20f,
                     PTR_s_No_gesture_control_items_receive_00467e60);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__setting_No_gesture_control_item_00467e64,
                            PTR_s__setting_No_gesture_control_item_00467e64);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                     PTR_s_setting_handle_gesture_control_l_00467e58,0x213,
                     PTR_s_Received_gesture_control_list__c_00467f18,bVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__setting_Received_gesture_contro_00467f1c,
                            PTR_s__setting_Received_gesture_contro_00467f1c,bVar1);
      }
      for (bVar4 = 0; bVar4 < bVar1; bVar4 = bVar4 + 1) {
        FUN_0046658e(*(uint *)(param_1 + (uint)bVar4 * 6 + 2) & 0xff,
                     *(uint *)(param_1 + (uint)bVar4 * 6 + 4) & 0xff,
                     *(undefined1 *)(param_1 + (uint)bVar4 * 6 + 6));
      }
      iVar2 = FUN_00466010();
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                     PTR_s_setting_handle_gesture_control_l_00467e58,0x227,
                     PTR_s_Updated_gesture_config__screen_o_00467f20,*(undefined1 *)(iVar2 + 5),
                     *(undefined1 *)(iVar2 + 6),*(undefined1 *)(iVar2 + 7),
                     *(undefined1 *)(iVar2 + 8),*(undefined1 *)(iVar2 + 9),
                     *(undefined1 *)(iVar2 + 10));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xd800000,PTR_s__setting_Updated_gesture_config__00467f24,
                            PTR_s__setting_Updated_gesture_config__00467f24,
                            *(undefined1 *)(iVar2 + 5),*(undefined1 *)(iVar2 + 6),
                            *(undefined1 *)(iVar2 + 7),*(undefined1 *)(iVar2 + 8),
                            *(undefined1 *)(iVar2 + 9),*(undefined1 *)(iVar2 + 10));
      }
      FUN_004661a6();
    }
  }
  return;
}

