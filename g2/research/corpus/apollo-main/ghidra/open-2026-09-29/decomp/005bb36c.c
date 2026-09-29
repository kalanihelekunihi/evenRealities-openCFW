
undefined4 FUN_005bb36c(int param_1,uint param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 *puVar2;
  byte *pbVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  byte bVar6;
  undefined1 uVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  byte *pbVar11;
  int iVar12;
  int iVar13;
  float fVar14;
  uint local_48;
  undefined *local_44;
  uint local_40;
  uint local_3c;
  uint local_38;
  uint local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  if (param_1 == 0) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      local_44 = PTR_s_layout4_create__parent_NULL_005bbce4;
      local_48 = 0x1ec;
      FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bbcf0,PTR_s_D__01_workspace_s200_ap510b_iar__005bbcec,
                   PTR_s_layout4_create_005bbce8);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__dashboard_wf_l4_layout4_create__005bbcf4,
                          PTR_s__dashboard_wf_l4_layout4_create__005bbcf4);
    }
    uVar9 = 0xffffffff;
  }
  else {
    iVar8 = FUN_005bafc4(param_3);
    pbVar3 = DAT_005bbd00;
    if (iVar8 == 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        local_44 = PTR_s_layout4_create__cfg_invalid__ret_005bbcf8;
        local_48 = 0x1f2;
        FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bbcf0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005bbcec,PTR_s_layout4_create_005bbce8);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__dashboard_wf_l4_layout4_create__005bbcfc,
                            PTR_s__dashboard_wf_l4_layout4_create__005bbcfc);
      }
      uVar9 = 0xffffffff;
    }
    else {
      pbVar11 = (byte *)(param_3 + 4);
      *DAT_005bbd00 = *pbVar11;
      *DAT_005bbcd4 = *(byte *)(param_3 + 5);
      FUN_0043c0e4(DAT_005bbcdc,0xc,0);
      iVar8 = DAT_005bbce0;
      FUN_0043c0e4(DAT_005bbce0,0x60,0);
      for (iVar13 = 0; iVar13 < (int)(uint)*DAT_005bbcd4; iVar13 = iVar13 + 1) {
        DAT_005bbcdc[iVar13] = *(float *)(pbVar11 + iVar13 * 4 + 4);
        FUN_0044b5a0(iVar13 * 0x20 + iVar8,pbVar11 + iVar13 * 0x20 + 0x11,0x1f);
        *(undefined1 *)(iVar13 * 0x20 + iVar8 + 0x1f) = 0;
      }
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        local_3c = (uint)*DAT_005bbcd4;
        local_40 = (uint)*pbVar3;
        local_44 = DAT_005bbd04;
        local_48 = 0x203;
        FUN_0043d574(3,PTR_s_dashboard_wf_l4_005bbcf0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005bbcec,PTR_s_layout4_create_005bbce8);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        local_48 = (uint)*DAT_005bbcd4;
        compress_log_output(0xc800000,DAT_005bbd08,DAT_005bbd08,*pbVar3);
      }
      iVar8 = UX_GetSystemBLEStatus();
      puVar4 = DAT_005bbd0c;
      local_38 = (uint)(iVar8 != 0);
      local_34 = param_2;
      uVar9 = FUN_0043de82(param_1);
      *puVar4 = uVar9;
      FUN_0043f4c0(*puVar4,200,0x120);
      FUN_0043f09a(*puVar4,local_34,0);
      uVar9 = FUN_0044104c(0);
      FUN_0044127e(*puVar4,uVar9,0);
      FUN_0044129e(*puVar4,0,0);
      FUN_0044131c(*puVar4,0,0);
      FUN_0044133a(*puVar4,0,0);
      FUN_00441378(*puVar4,0,0);
      FUN_00441386(*puVar4,0,0);
      FUN_005bab2c(*puVar4,0,0);
      FUN_0044146a(*puVar4,0,0);
      uVar9 = FUN_0044104c(0xffffff);
      FUN_0044140e(*puVar4,uVar9,0);
      FUN_0044142e(*puVar4,0xff,0);
      FUN_0043dfa4(*puVar4,0x10);
      FUN_005badf4(&local_2c,&local_30);
      iVar8 = DAT_005bbcd8;
      FUN_0043c0e4(DAT_005bbcd8,0x54,0);
      for (iVar13 = 0; puVar2 = DAT_005bbcd0, iVar13 < (int)(uint)*DAT_005bbcd4; iVar13 = iVar13 + 1
          ) {
        iVar12 = *(int *)(PTR_DAT_005bbd20 + iVar13 * 4);
        uVar9 = FUN_0043de82(*puVar4);
        FUN_0043f4c0(uVar9,0x3fffffff,0x3fffffff);
        FUN_0044129e(uVar9,0,0);
        FUN_0044131c(uVar9,0,0);
        FUN_0044133a(uVar9,0,0);
        FUN_00441386(uVar9,0,0);
        FUN_005bab2c(uVar9,0,0);
        FUN_0044146a(uVar9,0,0);
        FUN_0043dfa4(uVar9,0x10);
        *(undefined4 *)(iVar8 + iVar13 * 0x1c) = uVar9;
        uVar10 = FUN_00498668(uVar9);
        FUN_0043f506(uVar10,0x1a);
        FUN_0043f568(uVar10,0x1a);
        FUN_0043f09a(uVar10,0,0);
        FUN_0043ded4(uVar10,0x10000);
        FUN_0043dfa4(uVar10,0x10);
        *(undefined4 *)(iVar13 * 0x1c + iVar8 + 4) = uVar10;
        uVar10 = FUN_00498668(uVar9);
        FUN_0043f506(uVar10,0x1a);
        FUN_0043f568(uVar10,0x1a);
        FUN_0043f09a(uVar10,0x20,0);
        FUN_0043ded4(uVar10,0x10000);
        FUN_0043dfa4(uVar10,0x10);
        *(undefined4 *)(iVar13 * 0x1c + iVar8 + 8) = uVar10;
        FUN_005bab76(uVar9,iVar12);
        if ((iVar13 == 0) &&
           (fVar14 = (float)FUN_00577d08(*DAT_005bbcdc * DAT_005bbb18), (int)fVar14 == 0)) {
          bVar1 = true;
        }
        else {
          bVar1 = false;
        }
        if (bVar1) {
          uVar9 = FUN_0043de82(*puVar4);
          FUN_0043f4c0(uVar9,0x3fffffff,0x3fffffff);
          FUN_0044129e(uVar9,0,0);
          FUN_0044131c(uVar9,0,0);
          FUN_0044133a(uVar9,0,0);
          FUN_00441386(uVar9,0,0);
          FUN_005bab2c(uVar9,0,0);
          FUN_0044146a(uVar9,0,0);
          uVar10 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar9,uVar10,0);
          FUN_0044142e(uVar9,0xff,0);
          FUN_0043dfa4(uVar9,0x10);
          FUN_0048ba78(uVar9,0);
          FUN_0048ba92(uVar9,0,2,2);
          FUN_00441254(uVar9,6,0);
          *(undefined4 *)(iVar13 * 0x1c + iVar8 + 0xc) = uVar9;
          uVar10 = FUN_00498668(uVar9);
          FUN_0043ded4(uVar10,0x10000);
          FUN_0043dfa4(uVar10,0x10);
          FUN_00498680(uVar10,PTR_DAT_005bbd14);
          *(undefined4 *)(iVar13 * 0x1c + iVar8 + 0x10) = uVar10;
          uVar10 = FUN_00499416(uVar9);
          FUN_0043f506(uVar10,0x3fffffff);
          FUN_0043f568(uVar10,0x3fffffff);
          FUN_0044143e(uVar10,PTR_DAT_005bbd10,0);
          FUN_004411e4(uVar10,2,0);
          *(undefined4 *)(iVar13 * 0x1c + iVar8 + 0x14) = uVar10;
          FUN_005bab76(uVar9,iVar12 + 0x20);
        }
        else {
          uVar9 = FUN_00499416(*puVar4);
          FUN_0043f506(uVar9,0x3fffffff);
          FUN_0043f568(uVar9,0x3fffffff);
          FUN_0044143e(uVar9,PTR_DAT_005bbd10,0);
          *(undefined4 *)(iVar13 * 0x1c + iVar8 + 0x14) = uVar9;
          FUN_005bab76(uVar9,iVar12 + 0x20);
        }
        uVar9 = FUN_00499416(*puVar4);
        FUN_0043f506(uVar9,0x3fffffff);
        FUN_0043f568(uVar9,0x3fffffff);
        FUN_0044143e(uVar9,PTR_DAT_005bbd18,0);
        FUN_0043c0e4(&local_48,0x10,0);
        FUN_005baef0(DAT_005bbcdc[iVar13],&local_48,0x10);
        FUN_0049942e(uVar9,&local_48);
        uVar10 = FUN_0044104c(PTR_LAB_00555554_1_005bbd1c);
        FUN_0044140e(uVar9,uVar10,0);
        FUN_0044142e(uVar9,0xff,0);
        *(undefined4 *)(iVar8 + iVar13 * 0x1c + 0x18) = uVar9;
        FUN_005bab76(uVar9,iVar12 + 0x36);
        FUN_005bb208(iVar13,local_2c,local_30);
      }
      uVar9 = FUN_00498668(*puVar4);
      *puVar2 = uVar9;
      FUN_0043f506(*puVar2,0x3fffffff);
      FUN_0043f568(*puVar2,0x3fffffff);
      FUN_00498680(*puVar2,PTR_DAT_005bbd24);
      FUN_0043ded4(*puVar2,0x10000);
      FUN_0043dfa4(*puVar2,0x10);
      FUN_005bab76(*puVar2,0xf3);
      puVar2 = DAT_005bbd28;
      uVar9 = FUN_0043de82(*puVar4);
      *puVar2 = uVar9;
      FUN_0043f4c0(*puVar2,0x3fffffff,0x3fffffff);
      FUN_0044129e(*puVar2,0,0);
      FUN_0044131c(*puVar2,0,0);
      FUN_0044133a(*puVar2,0,0);
      FUN_00441386(*puVar2,0,0);
      FUN_005bab2c(*puVar2,0,0);
      FUN_0044146a(*puVar2,0,0);
      FUN_0043dfa4(*puVar2,0x10);
      FUN_0048ba78(*puVar2,0);
      FUN_0048ba92(*puVar2,0,2,2);
      FUN_00441254(*puVar2,0xc,0);
      puVar5 = DAT_005bbd2c;
      uVar9 = FUN_00498668(*puVar2);
      *puVar5 = uVar9;
      FUN_0043ded4(*puVar5,0x10000);
      FUN_0043dfa4(*puVar5,0x10);
      bVar6 = ui_common_api_fn_00509f8e();
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        local_40 = (uint)bVar6;
        local_44 = DAT_005bbd30;
        local_48 = 0x2b4;
        FUN_0043d574(4,PTR_s_dashboard_wf_l4_005bbcf0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005bbcec,PTR_s_layout4_create_005bbce8);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005bbd34,DAT_005bbd34,bVar6);
      }
      uVar9 = FUN_005baba6(bVar6);
      FUN_00498680(*puVar5,uVar9);
      iVar8 = FUN_0047d9c4();
      puVar5 = DAT_005bbd38;
      if (iVar8 != 0) {
        uVar9 = FUN_00498668(*puVar2);
        *puVar5 = uVar9;
        FUN_0043ded4(*puVar5,0x10000);
        FUN_0043dfa4(*puVar5,0x10);
        iVar8 = FUN_0047d9cc();
        if (iVar8 == 0) {
          FUN_00498680(*puVar5,PTR_DAT_005bbd3c);
        }
        else {
          uVar7 = FUN_0049c5bc();
          uVar9 = FUN_005bac42(uVar7);
          FUN_00498680(*puVar5,uVar9);
        }
      }
      FUN_0043f66c(*puVar4);
      iVar8 = FUN_0043fdda(*puVar2);
      FUN_005bab76(*puVar2,0x11e - iVar8);
      FUN_005bb1cc(local_38);
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        local_3c = local_38;
        local_40 = local_34;
        local_44 = PTR_s_layout4_created_at_x__d__ble__d__005bbd40;
        local_48 = 0x2ce;
        FUN_0043d574(3,PTR_s_dashboard_wf_l4_005bbcf0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005bbcec,PTR_s_layout4_create_005bbce8);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        local_48 = local_38;
        compress_log_output(0xc800000,PTR_s__dashboard_wf_l4_layout4_created_005bbd44,
                            PTR_s__dashboard_wf_l4_layout4_created_005bbd44,local_34);
      }
      uVar9 = 0;
    }
  }
  return uVar9;
}

