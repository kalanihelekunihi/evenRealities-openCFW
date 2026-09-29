
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 tracepoint_handle_ble_data(int param_1,undefined *param_2)

{
  byte bVar1;
  byte *pbVar2;
  byte bVar3;
  char cVar4;
  int iVar5;
  undefined4 uVar6;
  undefined *puVar7;
  uint uStack_38;
  undefined *puStack_34;
  undefined *puStack_30;
  uint uStack_2c;
  uint uStack_28;
  undefined1 auStack_24 [12];
  undefined *puStack_18;
  
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    bVar3 = tracepoint_role_char();
    uStack_2c = (uint)bVar3;
    puStack_34 = PTR_s_tracepoint_ble_data_len__u_role__005ef00c;
    uStack_38 = 0x1a9;
    puStack_30 = param_2;
    FUN_0043d574(4,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_handle_ble_data_005ef010);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    bVar3 = tracepoint_role_char();
    uStack_38 = (uint)bVar3;
    compress_log_output(0x10800000,_DAT_005ef01c,_DAT_005ef01c,param_2);
  }
  pbVar2 = _DAT_005ef020;
  if ((param_1 == 0) || (param_2 == (undefined *)0x0)) {
    uVar6 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(_DAT_005ef020,0x206,0);
    FUN_0048f49c(&uStack_38,param_1,param_2);
    FUN_00439c04(auStack_24,&uStack_38,0x10);
    cVar4 = FUN_00490120(auStack_24,DAT_005ef024,pbVar2);
    if (cVar4 == '\0') {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        puStack_30 = PTR_s__none__005ef028;
        if (puStack_18 != (undefined *)0x0) {
          puStack_30 = puStack_18;
        }
        puStack_34 = PTR_s_tracepoint_protobuf_decode_faile_005ef02c;
        uStack_38 = 0x1b5;
        FUN_0043d574(1,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_handle_ble_data_005ef010);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        puVar7 = PTR_s__none__005ef028;
        if (puStack_18 != (undefined *)0x0) {
          puVar7 = puStack_18;
        }
        compress_log_output(0x4400000,PTR_s__tp_setting_tracepoint_protobuf_d_005ef030,
                            PTR_s__tp_setting_tracepoint_protobuf_d_005ef030,puVar7);
      }
      uVar6 = 0xffffffff;
    }
    else {
      bVar3 = pbVar2[1];
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        uStack_28 = (uint)*(ushort *)(pbVar2 + 2);
        uStack_2c = (uint)bVar3;
        puStack_30 = (undefined *)(uint)*pbVar2;
        puStack_34 = PTR_s_tracepoint_recv_cmd__d_magic__u_w_005ef034;
        uStack_38 = 0x1bc;
        FUN_0043d574(4,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_handle_ble_data_005ef010);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        puStack_34 = (undefined *)(uint)*(ushort *)(pbVar2 + 2);
        uStack_38 = (uint)bVar3;
        compress_log_output(0x10c00000,PTR_s__tp_setting_tracepoint_recv_cmd__005ef038,
                            PTR_s__tp_setting_tracepoint_recv_cmd__005ef038,*pbVar2);
      }
      bVar1 = *pbVar2;
      if (bVar1 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          puStack_34 = PTR_s_tracepoint_heartbeat_005ef03c;
          uStack_38 = 0x1c0;
          FUN_0043d574(4,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_handle_ble_data_005ef010);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__tp_setting_tracepoint_heartbeat_005ef040,
                              PTR_s__tp_setting_tracepoint_heartbeat_005ef040);
        }
      }
      else if (bVar1 == 2) {
        if (*(short *)(pbVar2 + 2) == 4) {
          tracepoint_handle_delete_file(bVar3,pbVar2 + 4);
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            puStack_30 = (undefined *)(uint)*(ushort *)(pbVar2 + 2);
            puStack_34 = PTR_s_tracepoint_delete_file_missing_d_005ef044;
            uStack_38 = 0x1cd;
            FUN_0043d574(2,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_handle_ble_data_005ef010);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__tp_setting_tracepoint_delete_fi_005ef048,
                                PTR_s__tp_setting_tracepoint_delete_fi_005ef048,
                                *(undefined2 *)(pbVar2 + 2));
          }
        }
      }
      else if (bVar1 < 2) {
        tracepoint_handle_request_file_name(bVar3);
      }
      else if (bVar1 == 3) {
        tracepoint_handle_delete_all(bVar3);
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          puStack_30 = (undefined *)(uint)*pbVar2;
          puStack_34 = PTR_s_tracepoint_unknown_cmd__d_005ef04c;
          uStack_38 = 0x1d6;
          FUN_0043d574(2,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_handle_ble_data_005ef010);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__tp_setting_tracepoint_unknown_c_005ef050,
                              PTR_s__tp_setting_tracepoint_unknown_c_005ef050,*pbVar2);
        }
      }
      uVar6 = 0;
    }
  }
  return uVar6;
}

