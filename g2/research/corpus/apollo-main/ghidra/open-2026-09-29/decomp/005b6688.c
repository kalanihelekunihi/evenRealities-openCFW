
undefined4
conversate_ui_action_tag_manual_shrink
          (undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined1 auStack_40 [8];
  undefined4 uStack_38;
  undefined4 uStack_30;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  iVar4 = DAT_005b6958;
  if (*(int *)(DAT_005b6958 + 0x1c) == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    uStack_1c = param_4;
    if (param_2 == 1) {
      FUN_005969a4();
    }
    *(bool *)(iVar4 + 0xa5) = param_2 == 2;
    iVar3 = osKernelGetTickCount();
    *(int *)(iVar4 + 0xa8) = iVar3 - *(int *)(iVar4 + 0xa8);
    APP_PbConversateTxEncodeTagTrackingData(iVar4 + 0xa0);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005b6950,DAT_005b694c,PTR_s_conversate_ui_action_tag_to_main_005b69a8,0x198
                   ,PTR_s_tracking_data_send__tag_id___d__o_005b69a4,*(undefined4 *)(iVar4 + 0xa0),
                   *(undefined1 *)(iVar4 + 0xa4),*(undefined1 *)(iVar4 + 0xa5),
                   *(undefined4 *)(iVar4 + 0xa8));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xd000000,PTR_s__conversate_ui_tracking_data_sen_005b69ac,
                          PTR_s__conversate_ui_tracking_data_sen_005b69ac,
                          *(undefined4 *)(iVar4 + 0xa0),*(undefined1 *)(iVar4 + 0xa4),
                          *(undefined1 *)(iVar4 + 0xa5),*(undefined4 *)(iVar4 + 0xa8));
    }
    *(undefined1 *)(iVar4 + 0x98) = 1;
    if (*(char *)(iVar4 + 0xa4) == '\x01') {
      FUN_0058c426(*(undefined4 *)(iVar4 + 0x1c),300,0);
      FUN_0058c238(*(undefined4 *)(iVar4 + 8),300,
                   PTR_conversate_ui_action_tag_to_main_page_1_005b69b0);
      uVar2 = 0;
    }
    else {
      uVar2 = FUN_0044dce2(*(undefined4 *)(iVar4 + 0x1c),1);
      FUN_0058c426(uVar2,200,0);
      FUN_0058c328(*(undefined4 *)(iVar4 + 8),300,200,0);
      if (*(int *)(iVar4 + 0x80) == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005b6950,DAT_005b694c,PTR_s_conversate_ui_action_tag_to_main_005b69a8,
                       0x1a7,PTR_s_tag_manual_shrink_failed__curren_005b69b4);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__conversate_ui_tag_manual_shrink_005b69b8,
                              PTR_s__conversate_ui_tag_manual_shrink_005b69b8);
        }
        uVar2 = 0xffffffff;
      }
      else {
        *(undefined4 *)(iVar4 + 0x88) = *(undefined4 *)(iVar4 + 0x80);
        FUN_00441488(*(undefined4 *)(iVar4 + 0x80),0,0);
        FUN_0043c0e4(&uStack_50,0x10,0);
        FUN_0043fc2a(*(undefined4 *)(iVar4 + 0x80),&uStack_50);
        uVar1 = uStack_4c;
        uVar2 = uStack_50;
        uVar5 = FUN_00451598(&uStack_50);
        uVar6 = FUN_004515a4(&uStack_50);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005b6950,DAT_005b694c,PTR_s_conversate_ui_action_tag_to_main_005b69a8,
                       0x1b6,PTR_s_tag_shrink_target__rel__d__d__d__005b69bc,uVar2,uVar1,uVar5,uVar6
                       ,uStack_50,uStack_4c,uStack_48,uStack_44);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xe000000,PTR_s__conversate_ui_tag_shrink_target_005b69c0,
                              PTR_s__conversate_ui_tag_shrink_target_005b69c0,uVar2,uVar1,uVar5,
                              uVar6,uStack_50,uStack_4c,uStack_48,uStack_44);
        }
        FUN_00439c04(auStack_40,PTR_DAT_005b69c4,0x24);
        uStack_38 = uVar2;
        uStack_30 = uVar1;
        uStack_28 = uVar5;
        uStack_24 = FUN_0043fdda(*(undefined4 *)(iVar4 + 0x1c));
        uStack_20 = uVar6;
        FUN_005b7704(*(undefined4 *)(iVar4 + 0x1c),auStack_40,
                     PTR_conversate_tag_page_deinit_1_005b69c8);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005b6950,DAT_005b694c,PTR_s_conversate_ui_action_tag_to_main_005b69a8,
                       0x1c5,PTR_s_tag_manual_shrink_animation_star_005b69cc);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__conversate_ui_tag_manual_shrink_005b69d0,
                              PTR_s__conversate_ui_tag_manual_shrink_005b69d0);
        }
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

