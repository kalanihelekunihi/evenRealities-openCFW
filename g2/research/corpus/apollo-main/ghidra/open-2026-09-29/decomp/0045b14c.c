
undefined4
FUN_0045b14c(undefined4 param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  char cVar2;
  ushort uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uStack_98;
  undefined *puStack_94;
  uint uStack_90;
  uint uStack_8c;
  undefined1 *puStack_88;
  undefined2 uStack_84;
  undefined2 auStack_78 [4];
  int iStack_70;
  undefined2 uStack_6c;
  undefined2 auStack_60 [4];
  int iStack_58;
  undefined2 uStack_54;
  undefined2 auStack_48 [4];
  int iStack_40;
  undefined2 uStack_3c;
  undefined2 auStack_30 [4];
  undefined **ppuStack_28;
  undefined2 uStack_24;
  undefined4 uStack_18;
  
  uVar1 = **(undefined1 **)(param_2 + 4);
  cVar2 = *(char *)(*(int *)(param_2 + 4) + 1);
  uStack_18 = param_4;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uStack_90 = (uint)(ushort)param_2[6];
    puStack_94 = PTR_s_Received_slave_send_sync_data_le_0045bc7c;
    uStack_98 = 0x19f;
    FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                 PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__sync_module_framework_Received_s_0045bc8c,
                        PTR_s__sync_module_framework_Received_s_0045bc8c,param_2[6]);
  }
  for (uVar5 = 0; (int)uVar5 < (int)(uint)(ushort)param_2[6]; uVar5 = uVar5 + 1) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_8c = (uint)*(byte *)(*(int *)(param_2 + 4) + uVar5);
      puStack_94 = PTR_s_data__d_____d_0045bc90;
      uStack_98 = 0x1a1;
      uStack_90 = uVar5;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      uStack_98 = (uint)*(byte *)(*(int *)(param_2 + 4) + uVar5);
      compress_log_output(0x10800000,PTR_s__sync_module_framework_data__d____0045bc94,
                          PTR_s__sync_module_framework_data__d____0045bc94,uVar5);
    }
  }
  if (cVar2 == '\x01') {
    iVar4 = *(int *)(param_2 + 4);
    uVar3 = *(ushort *)(iVar4 + 2);
    FUN_00464b2e(uVar3,iVar4 + 8,*(undefined2 *)(iVar4 + 6),0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_90 = (uint)uVar3;
      puStack_94 = PTR_s_received_slave_send_display_star_0045bc98;
      uStack_98 = 0x1dc;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_s_0045bc9c,
                          PTR_s__sync_module_framework_received_s_0045bc9c,uVar3);
    }
    FUN_0043c0e4(auStack_78,0x18,0);
    uStack_98._0_2_ = CONCAT11(0xb,(undefined1)uStack_98);
    iStack_70 = (int)&uStack_98 + 1;
    uStack_6c = 1;
    auStack_78[0] = *param_2;
    for (iVar4 = 0; iVar4 < (int)(uint)(ushort)param_2[6]; iVar4 = iVar4 + 1) {
    }
    FUN_0049225a(param_1,auStack_78);
  }
  else if (cVar2 == '\x03') {
    iVar4 = *(int *)(param_2 + 4);
    uVar3 = *(ushort *)(iVar4 + 2);
    FUN_00464bb2(uVar3,iVar4 + 8,*(undefined2 *)(iVar4 + 6),0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_90 = (uint)uVar3;
      puStack_94 = PTR_s_received_slave_send_display_star_0045bc98;
      uStack_98 = 0x1a9;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_s_0045bc9c,
                          PTR_s__sync_module_framework_received_s_0045bc9c,uVar3);
    }
    FUN_0043c0e4(auStack_30,0x18,0);
    puStack_94 = (undefined *)CONCAT31(puStack_94._1_3_,0xb);
    ppuStack_28 = &puStack_94;
    uStack_24 = 1;
    auStack_30[0] = *param_2;
    for (iVar4 = 0; iVar4 < (int)(uint)(ushort)param_2[6]; iVar4 = iVar4 + 1) {
    }
    FUN_0049225a(param_1,auStack_30);
  }
  else if (cVar2 == '\x05') {
    iVar4 = *(int *)(param_2 + 4);
    uVar3 = *(ushort *)(iVar4 + 2);
    FUN_00464c36(uVar3,iVar4 + 8,*(undefined2 *)(iVar4 + 6),0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_90 = (uint)uVar3;
      puStack_94 = PTR_s_received_slave_send_display_star_0045bc98;
      uStack_98 = 0x1ba;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_s_0045bc9c,
                          PTR_s__sync_module_framework_received_s_0045bc9c,uVar3);
    }
    FUN_0043c0e4(auStack_48,0x18,0);
    uStack_98 = CONCAT13(0xb,(undefined3)uStack_98);
    iStack_40 = (int)&uStack_98 + 3;
    uStack_3c = 1;
    auStack_48[0] = *param_2;
    for (iVar4 = 0; iVar4 < (int)(uint)(ushort)param_2[6]; iVar4 = iVar4 + 1) {
    }
    FUN_0049225a(param_1,auStack_48);
  }
  else if (cVar2 == '\a') {
    iVar4 = *(int *)(param_2 + 4);
    uVar3 = *(ushort *)(iVar4 + 2);
    FUN_00465748(uVar3,*(undefined4 *)(iVar4 + 4),*(undefined4 *)(iVar4 + 8),0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_90 = (uint)uVar3;
      puStack_94 = DAT_0045be64;
      uStack_98 = 0x1f0;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0045be68,DAT_0045be68,uVar3);
    }
    FUN_0043c0e4(&uStack_90,0x18,0);
    uStack_98 = CONCAT31(uStack_98._1_3_,0xb);
    uStack_84 = 1;
    uStack_90 = CONCAT22(uStack_90._2_2_,*param_2);
    for (iVar4 = 0; iVar4 < (int)(uint)(ushort)param_2[6]; iVar4 = iVar4 + 1) {
    }
    puStack_88 = (undefined1 *)&uStack_98;
    FUN_0049225a(param_1,&uStack_90);
  }
  else if (cVar2 == '\x10') {
    uVar3 = *(ushort *)(*(int *)(param_2 + 4) + 2);
    FUN_00464cba(0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_90 = (uint)uVar3;
      puStack_94 = PTR_s_received_slave_send_display_star_0045bc98;
      uStack_98 = 0x1cb;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sync_module_framework_received_s_0045bc9c,
                          PTR_s__sync_module_framework_received_s_0045bc9c,uVar3);
    }
    FUN_0043c0e4(auStack_60,0x18,0);
    uStack_98._0_3_ = CONCAT12(0xb,(undefined2)uStack_98);
    iStack_58 = (int)&uStack_98 + 2;
    uStack_54 = 1;
    auStack_60[0] = *param_2;
    for (iVar4 = 0; iVar4 < (int)(uint)(ushort)param_2[6]; iVar4 = iVar4 + 1) {
    }
    FUN_0049225a(param_1,auStack_60);
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_90 = (uint)CONCAT11(cVar2,uVar1);
      puStack_94 = DAT_0045bbf0;
      uStack_98 = 0x1ff;
      FUN_0043d574(2,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                   PTR_s_MasterScheduleModuleDataReplyLis_0045bc80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__sync_module_framework_unknown_c_0045bc78,
                          PTR_s__sync_module_framework_unknown_c_0045bc78,CONCAT11(cVar2,uVar1));
    }
  }
  return 1;
}

