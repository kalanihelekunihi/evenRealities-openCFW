
undefined4
FUN_0045adf4(undefined4 param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  char cVar2;
  int iVar3;
  ushort *puVar4;
  undefined4 local_80;
  undefined *local_7c;
  uint local_78;
  undefined1 *local_74;
  undefined2 local_70;
  undefined2 local_64 [4];
  int local_5c;
  undefined2 local_58;
  undefined2 local_4c [4];
  int local_44;
  undefined2 local_40;
  undefined2 local_34 [4];
  int local_2c;
  undefined2 local_28;
  undefined4 uStack_1c;
  
  puVar4 = *(ushort **)(param_2 + 4);
  uStack_1c = param_4;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    local_78 = (uint)(ushort)param_2[6];
    local_7c = DAT_0045b84c;
    local_80 = 0x149;
    FUN_0043d574(4,DAT_0045b100,DAT_0045b0fc,PTR_s_SlaveDispalyCommandReplyListener_0045ba28);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__sync_module_framework_Received_d_0045ba2c,
                        PTR_s__sync_module_framework_Received_d_0045ba2c,param_2[6]);
  }
  cVar2 = (char)(*puVar4 >> 8);
  if (cVar2 == '\x01') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_78 = (uint)(ushort)param_2[6];
      local_7c = PTR_s_received_display_start_command_l_0045ba30;
      local_80 = 0x14d;
      FUN_0043d574(4,DAT_0045b100,DAT_0045b0fc,PTR_s_SlaveDispalyCommandReplyListener_0045ba28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_d_0045ba34,
                          PTR_s__sync_module_framework_received_d_0045ba34,param_2[6]);
    }
    uVar1 = puVar4[1];
    FUN_0043c0e4(local_34,0x18,0);
    local_80 = CONCAT13(2,(undefined3)local_80);
    local_2c = (int)&local_80 + 3;
    local_28 = 1;
    local_34[0] = *param_2;
    for (iVar3 = 0; iVar3 < (int)(uint)(ushort)param_2[6]; iVar3 = iVar3 + 1) {
    }
    FUN_0049225a(param_1,local_34);
    FUN_004441ec(uVar1,puVar4 + 4,puVar4[3]);
  }
  else if (cVar2 == '\x03') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_78 = (uint)(ushort)param_2[6];
      local_7c = PTR_s_received_display_refresh_command_0045ba38;
      local_80 = 0x15e;
      FUN_0043d574(4,DAT_0045b100,DAT_0045b0fc,PTR_s_SlaveDispalyCommandReplyListener_0045ba28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0045bae8,DAT_0045bae8,param_2[6]);
    }
    uVar1 = puVar4[1];
    FUN_0043c0e4(local_4c,0x18,0);
    local_80._0_3_ = CONCAT12(4,(undefined2)local_80);
    local_44 = (int)&local_80 + 2;
    local_40 = 1;
    local_4c[0] = *param_2;
    for (iVar3 = 0; iVar3 < (int)(uint)(ushort)param_2[6]; iVar3 = iVar3 + 1) {
    }
    FUN_0049225a(param_1,local_4c);
    FUN_004442d0(uVar1,puVar4 + 4,puVar4[3]);
  }
  else if (cVar2 == '\x05') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_78 = (uint)(ushort)param_2[6];
      local_7c = DAT_0045baec;
      local_80 = 0x16f;
      FUN_0043d574(4,DAT_0045b100,DAT_0045b0fc,PTR_s_SlaveDispalyCommandReplyListener_0045ba28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0045bb54,DAT_0045bb54,param_2[6]);
    }
    uVar1 = puVar4[1];
    FUN_0043c0e4(local_64,0x18,0);
    local_80._0_2_ = CONCAT11(6,(undefined1)local_80);
    local_5c = (int)&local_80 + 1;
    local_58 = 1;
    local_64[0] = *param_2;
    for (iVar3 = 0; iVar3 < (int)(uint)(ushort)param_2[6]; iVar3 = iVar3 + 1) {
    }
    FUN_0049225a(param_1,local_64);
    FUN_004443cc(uVar1,puVar4 + 4,puVar4[3]);
  }
  else if (cVar2 == '\x10') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_78 = (uint)(ushort)param_2[6];
      local_7c = DAT_0045baec;
      local_80 = 0x181;
      FUN_0043d574(4,DAT_0045b100,DAT_0045b0fc,PTR_s_SlaveDispalyCommandReplyListener_0045ba28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0045bb54,DAT_0045bb54,param_2[6]);
    }
    FUN_0043c0e4(&local_7c,0x18,0);
    local_80 = CONCAT31(local_80._1_3_,0x11);
    local_70 = 1;
    local_7c = (undefined *)CONCAT22(local_7c._2_2_,*param_2);
    for (iVar3 = 0; iVar3 < (int)(uint)(ushort)param_2[6]; iVar3 = iVar3 + 1) {
    }
    local_74 = (undefined1 *)&local_80;
    FUN_0049225a(param_1,&local_7c);
    FUN_004444b8(puVar4 + 4,puVar4[3]);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_78 = (uint)*puVar4;
      local_7c = DAT_0045bbf0;
      local_80 = 0x193;
      FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,PTR_s_SlaveDispalyCommandReplyListener_0045ba28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__sync_module_framework_unknown_c_0045bc78,
                          PTR_s__sync_module_framework_unknown_c_0045bc78,*puVar4);
    }
  }
  return 1;
}

