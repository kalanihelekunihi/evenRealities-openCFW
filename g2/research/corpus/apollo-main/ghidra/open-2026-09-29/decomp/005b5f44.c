
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
conversate_ui_action_tag_show(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  undefined *puVar3;
  undefined1 uVar4;
  undefined1 *puVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined *puVar11;
  undefined *puVar12;
  int iVar13;
  undefined4 uStack_60;
  undefined *puStack_5c;
  undefined *puStack_58;
  undefined *puStack_54;
  undefined *puStack_50;
  undefined *puStack_4c;
  undefined *puStack_48;
  undefined *puStack_44;
  undefined *puStack_40;
  undefined *puStack_3c;
  undefined *puStack_38;
  undefined *puStack_34;
  undefined *puStack_30;
  undefined *puStack_2c;
  undefined4 uStack_28;
  
  iVar1 = DAT_005b6958;
  uStack_28 = param_4;
  if (param_2 == 0) {
    puVar5 = (undefined1 *)FUN_005964e2(*(uint *)(DAT_005b6958 + 0x84) & 0xffff);
  }
  else {
    puVar5 = (undefined1 *)FUN_00596930();
  }
  if (puVar5 == (undefined1 *)0x0) {
    uVar6 = 0xffffffff;
  }
  else {
    *(undefined4 *)(iVar1 + 0xa0) = *(undefined4 *)(puVar5 + 0x10);
    *(bool *)(iVar1 + 0xa4) = param_2 != 0;
    uVar6 = osKernelGetTickCount();
    *(undefined4 *)(iVar1 + 0xa8) = uVar6;
    if (*(int *)(iVar1 + 0x1c) == 0) {
      uVar6 = FUN_0043de82(*_DAT_005b6968);
      *(undefined4 *)(iVar1 + 0x1c) = uVar6;
    }
    else {
      FUN_0044d878(*(undefined4 *)(iVar1 + 0x1c));
    }
    FUN_0043f4c0(*(undefined4 *)(iVar1 + 0x1c),0x240,0x3fffffff);
    FUN_0043f6ac(*(undefined4 *)(iVar1 + 0x1c),1);
    FUN_004411aa(*(undefined4 *)(iVar1 + 0x1c),*(undefined4 *)(iVar1 + 0x90),0);
    FUN_0044129e(*(undefined4 *)(iVar1 + 0x1c),0,0);
    FUN_0044131c(*(undefined4 *)(iVar1 + 0x1c),1,0);
    FUN_0044130c(*(undefined4 *)(iVar1 + 0x1c),0xff,0);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_004412ec(*(undefined4 *)(iVar1 + 0x1c),uVar6,0);
    FUN_0044146a(*(undefined4 *)(iVar1 + 0x1c),6,0);
    FUN_0044122a(*(undefined4 *)(iVar1 + 0x1c),0xc,0);
    FUN_00441238(*(undefined4 *)(iVar1 + 0x1c),0,0);
    FUN_0044120e(*(undefined4 *)(iVar1 + 0x1c),6,0);
    FUN_0044121c(*(undefined4 *)(iVar1 + 0x1c),6,0);
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1c),0x10);
    uVar6 = FUN_0043de82(*(undefined4 *)(iVar1 + 0x1c));
    FUN_0043f4c0(uVar6,0x228,0x1c);
    FUN_0043f6ac(uVar6,1);
    FUN_0044129e(uVar6,0,0);
    FUN_0044131c(uVar6,0,0);
    FUN_0044146a(uVar6,0,0);
    conversate_ui_menu_apply_base_style(uVar6,0,0);
    FUN_0043dfa4(uVar6,0x10);
    uVar7 = FUN_00498668(uVar6);
    uVar8 = func_0x005b0af6(*puVar5);
    FUN_00498680(uVar7,uVar8);
    uVar8 = FUN_0044104c(0);
    FUN_0044127e(uVar7,uVar8,0);
    FUN_0044129e(uVar7,0xff,0);
    FUN_004413ce(uVar7,0xff,0);
    FUN_0043f6ac(uVar7,7);
    uVar8 = FUN_00499416(uVar6);
    FUN_0049942e(uVar8,*(undefined4 *)(puVar5 + 4));
    FUN_0044143e(uVar8,*_DAT_005b696c,0);
    FUN_00441180(uVar8,0x1fe,0);
    FUN_004411aa(uVar8,0x1c,0);
    FUN_00499678(uVar8,1);
    FUN_0044145a(uVar8,1,0);
    uVar9 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar8,uVar9,0);
    uStack_60 = (undefined *)0xffffffff;
    FUN_0043f6d6(uVar8,uVar7,0x14,8);
    uVar7 = FUN_0043de82(*(undefined4 *)(iVar1 + 0x1c));
    FUN_0043f4c0(uVar7,0x20a,0x3fffffff);
    uStack_60 = (undefined *)0xa;
    FUN_0043f6d6(uVar7,uVar8,0xd,0);
    FUN_0044129e(uVar7,0,0);
    FUN_0044131c(uVar7,0,0);
    FUN_0044130c(uVar7,0,0);
    FUN_0044146a(uVar7,0,0);
    conversate_ui_menu_apply_base_style(uVar7,0,0);
    FUN_0044e368(uVar7,3);
    FUN_0043ded4(uVar7,0x10);
    FUN_0044e3ca(uVar7,0xc);
    FUN_0043dfa4(uVar7,0x360);
    FUN_004411aa(uVar7,((*(int *)(iVar1 + 0x90) + -0x26) / 0x1c) * 0x1c,0);
    uVar9 = FUN_00499416(uVar7);
    FUN_0043f4c0(uVar9,0x1fe,0x3fffffff);
    FUN_0044144c(uVar9,0x1c - *(int *)(*_DAT_005b696c + 0xc),0);
    FUN_0043f6b8(uVar9,1,0,0);
    FUN_00499678(uVar9,0);
    uVar10 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar9,uVar10,0);
    FUN_0044143e(uVar9,*_DAT_005b696c,0);
    FUN_0044145a(uVar9,1,0);
    FUN_0049942e(uVar9,*(undefined4 *)(puVar5 + 8));
    *(undefined1 *)(iVar1 + 0x98) = 1;
    if (param_2 != 0) {
      if (*(char *)(iVar1 + 0x94) == '\0') {
        uVar4 = conversate_ui_action_menu_page_scroll_down(uVar9);
      }
      else {
        uVar4 = *(undefined1 *)(iVar1 + 0x94);
      }
      *(undefined1 *)(iVar1 + 0x95) = uVar4;
      uVar6 = FUN_00499416(uVar6);
      puVar2 = PTR_s_ID_CONVERSATE_CLOSE_IN_X_SEC_005b6970;
      uVar9 = FUN_00460084(PTR_s_ID_CONVERSATE_CLOSE_IN_X_SEC_005b6970);
      uVar9 = FUN_0045fffe(puVar2,uVar9);
      FUN_0049954c(uVar6,uVar9,*(undefined1 *)(iVar1 + 0x95));
      FUN_0044143e(uVar6,*_DAT_005b696c,0);
      FUN_0043f4c0(uVar6,0x3fffffff,0x3fffffff);
      uVar9 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar6,uVar9,0);
      FUN_0044145a(uVar6,1,0);
      FUN_0043f6b8(uVar6,8,0xfffffff6,0);
      FUN_00441180(uVar8,400,0);
    }
    FUN_0058c426(*(undefined4 *)(iVar1 + 8),200,0);
    FUN_0043f66c(*(undefined4 *)(iVar1 + 0x1c));
    FUN_0043c0e4(&puStack_38,0x10,0);
    FUN_0043fc2a(*(undefined4 *)(iVar1 + 0x80),&puStack_38);
    puVar3 = puStack_34;
    puVar2 = puStack_38;
    puVar11 = (undefined *)FUN_00451598(&puStack_38);
    puVar12 = (undefined *)FUN_004515a4(&puStack_38);
    iVar13 = FUN_0043d0ce();
    if (iVar13 << 0x1e < 0) {
      puStack_3c = puStack_2c;
      puStack_40 = puStack_30;
      puStack_44 = puStack_34;
      puStack_48 = puStack_38;
      puStack_54 = puVar3;
      puStack_58 = puVar2;
      puStack_5c = PTR_s_tag_expand_source__rel__d__d__d__005b6974;
      uStack_60 = (undefined *)0xeb;
      puStack_50 = puVar11;
      puStack_4c = puVar12;
      FUN_0043d574(3,DAT_005b6950,DAT_005b694c,PTR_s_conversate_ui_action_tag_show_005b6978);
    }
    iVar13 = FUN_0043d0ce();
    if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
      puStack_48 = puStack_2c;
      puStack_4c = puStack_30;
      puStack_50 = puStack_34;
      puStack_54 = puStack_38;
      uStack_60 = puVar3;
      puStack_5c = puVar11;
      puStack_58 = puVar12;
      compress_log_output(0xe000000,PTR_s__conversate_ui_tag_expand_source_005b697c,
                          PTR_s__conversate_ui_tag_expand_source_005b697c,puVar2);
    }
    FUN_00439c04(&uStack_60,PTR_DAT_005b6980,0x24);
    puStack_5c = puVar2;
    puStack_54 = puVar3;
    puStack_4c = puVar11;
    puStack_44 = puVar12;
    puStack_40 = (undefined *)FUN_0043fdda(*(undefined4 *)(iVar1 + 0x1c));
    if (param_2 == 0) {
      uStack_60 = (undefined *)CONCAT22(200,(undefined2)uStack_60);
    }
    else {
      FUN_0058c238(*(undefined4 *)(iVar1 + 0x1c),200,0);
      uStack_60 = (undefined *)CONCAT22(500,(undefined2)uStack_60);
    }
    FUN_0043ded4(uVar7,1);
    FUN_005b7704(*(undefined4 *)(iVar1 + 0x1c),&uStack_60,
                 PTR_conversate_tag_close_timer_callback_1_005b6984);
    uVar6 = 0;
  }
  return uVar6;
}

