
undefined4 FUN_0045b850(undefined4 param_1,undefined2 *param_2)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  ushort *puVar5;
  undefined4 local_38;
  undefined *local_34;
  uint local_30;
  undefined1 *local_2c;
  undefined2 local_28;
  
  puVar5 = *(ushort **)(param_2 + 4);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_30 = (uint)(ushort)param_2[6];
    local_34 = PTR_s_Received_input_event_command_len_0045bf94;
    local_38 = 0x245;
    FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                 PTR_s_SlaveInputEventReplyListener_0045bf98);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__sync_module_framework_Received_i_0045bf9c,
                        PTR_s__sync_module_framework_Received_i_0045bf9c,param_2[6]);
  }
  if (*puVar5 >> 8 == 7) {
    uVar1 = puVar5[1];
    uVar3 = *(uint *)(puVar5 + 2);
    uVar4 = *(uint *)(puVar5 + 4);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_30 = (uint)uVar1;
      local_34 = PTR_s_received_input_event_command_inp_0045bfa0;
      local_38 = 0x24b;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_SlaveInputEventReplyListener_0045bf98);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_i_0045bfa4,
                          PTR_s__sync_module_framework_received_i_0045bfa4,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_34 = PTR_s_received_input_event_command_inp_0045bfa8;
      local_38 = 0x24c;
      local_30 = uVar3;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_SlaveInputEventReplyListener_0045bf98);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_i_0045bfac,
                          PTR_s__sync_module_framework_received_i_0045bfac,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_34 = PTR_s_received_input_event_command_inp_0045bfb0;
      local_38 = 0x24d;
      local_30 = uVar4;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_SlaveInputEventReplyListener_0045bf98);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_i_0045bfb4,
                          PTR_s__sync_module_framework_received_i_0045bfb4,uVar4);
    }
    FUN_0043c0e4(&local_34,0x18,0);
    local_38 = CONCAT31(local_38._1_3_,8);
    local_28 = 1;
    local_34 = (undefined *)CONCAT22(local_34._2_2_,*param_2);
    local_2c = (undefined1 *)&local_38;
    FUN_0049225a(param_1,&local_34);
    FUN_004445a4(uVar1,uVar3,uVar4);
    return 1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_30 = (uint)*puVar5;
    local_34 = DAT_0045bbf0;
    local_38 = 0x259;
    FUN_0043d574(2,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                 PTR_s_SlaveInputEventReplyListener_0045bf98);
  }
  iVar2 = FUN_0043d0ce();
  if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
    return 1;
  }
  compress_log_output(0x8400000,PTR_s__sync_module_framework_unknown_c_0045bc78,
                      PTR_s__sync_module_framework_unknown_c_0045bc78,*puVar5);
  return 1;
}

