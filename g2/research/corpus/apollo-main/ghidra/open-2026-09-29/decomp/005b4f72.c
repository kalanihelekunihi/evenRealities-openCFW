
undefined4 FUN_005b4f72(undefined4 param_1,byte *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_2 == (byte *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_tag_data_005b567c,0x105,
                   PTR_s_conversate_tag_data_is_NULL_005b5678);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_conversate_tag_data_i_005b5680);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_tag_data_005b567c,0x10a,
                   PTR_s_tag_data_received_type___d__len__005b5684,*param_2,
                   *(undefined2 *)(param_2 + 2),*(undefined2 *)(param_2 + 0x84),param_2 + 4,
                   param_2 + 0x86);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xd400000,PTR_s__conversate_tag_data_received_ty_005b5688,
                          PTR_s__conversate_tag_data_received_ty_005b5688,*param_2,
                          *(undefined2 *)(param_2 + 2),*(undefined2 *)(param_2 + 0x84),param_2 + 4,
                          param_2 + 0x86);
    }
    if ((*param_2 == 0) || (4 < *param_2)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_tag_data_005b567c,0x10d,
                     PTR_s_Invalid_tag_type___d_005b568c,*param_2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__conversate_Invalid_tag_type___d_005b5690,
                            PTR_s__conversate_Invalid_tag_type___d_005b5690,*param_2);
      }
      uVar2 = 0xffffffff;
    }
    else if ((*(short *)(param_2 + 2) == 0) || (*(short *)(param_2 + 0x84) == 0)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_tag_data_005b567c,0x112,
                     PTR_s_Invalid_tag_text___s___s_005b5694,param_2 + 4,param_2 + 0x86);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__conversate_Invalid_tag_text___s_005b5698,
                            PTR_s__conversate_Invalid_tag_text___s_005b5698,param_2 + 4,
                            param_2 + 0x86);
      }
      uVar2 = 0xffffffff;
    }
    else {
      iVar1 = FUN_00596360(param_2);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_tag_data_005b567c,0x118,
                       PTR_s_Failed_to_store_tag_data_005b569c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__conversate_Failed_to_store_tag_d_005b56a0,
                              PTR_s__conversate_Failed_to_store_tag_d_005b56a0);
        }
        uVar2 = 0xffffffff;
      }
      else {
        FUN_005b02e4(5,0);
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

