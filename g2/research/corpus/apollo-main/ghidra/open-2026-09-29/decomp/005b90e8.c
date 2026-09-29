
undefined4 FUN_005b90e8(int param_1,uint param_2,char *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  byte *pbVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  byte bVar6;
  undefined1 uVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  uint local_68;
  undefined *local_64;
  uint local_60;
  uint local_5c;
  uint local_58;
  uint local_54;
  char local_50 [4];
  undefined1 auStack_4c [4];
  int local_48;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  if (param_1 == 0) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      local_64 = PTR_s_layout2_create__parent_NULL_005b9c64;
      local_68 = 0x139;
      FUN_0043d574(1,PTR_s_dashboard_wf_l2_005b9c70,PTR_s_D__01_workspace_s200_ap510b_iar__005b9c6c,
                   PTR_s_layout2_create_005b9c68);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__dashboard_wf_l2_layout2_create__005b9c74,
                          PTR_s__dashboard_wf_l2_layout2_create__005b9c74);
    }
    uVar9 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(local_50,3,0);
    if ((param_3 == (char *)0x0) || (*param_3 != '\x02')) {
      *DAT_005b9c78 = 0;
      *DAT_005b9c7c = 1;
      *DAT_005b9afc = 1;
      *DAT_005b9c60 = 0;
    }
    else {
      *DAT_005b9c78 = param_3[5];
      *DAT_005b9c7c = param_3[6];
      *DAT_005b9afc = param_3[4];
      pbVar3 = DAT_005b9c60;
      *DAT_005b9c60 = param_3[7];
      if (3 < *pbVar3) {
        *pbVar3 = 3;
      }
      for (iVar8 = 0; iVar8 < (int)(uint)*pbVar3; iVar8 = iVar8 + 1) {
        local_50[iVar8] = param_3[iVar8 + 8];
      }
    }
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      local_54 = (uint)*DAT_005b9c60;
      local_58 = (uint)*DAT_005b9c7c;
      local_5c = (uint)*DAT_005b9c78;
      local_60 = (uint)*DAT_005b9afc;
      local_64 = DAT_005b9c80;
      local_68 = 0x154;
      FUN_0043d574(3,PTR_s_dashboard_wf_l2_005b9c70,PTR_s_D__01_workspace_s200_ap510b_iar__005b9c6c,
                   PTR_s_layout2_create_005b9c68);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      local_60 = (uint)*DAT_005b9c60;
      local_64 = (undefined *)(uint)*DAT_005b9c7c;
      local_68 = (uint)*DAT_005b9c78;
      compress_log_output(0xd000000,DAT_005b9c84,DAT_005b9c84,*DAT_005b9afc);
    }
    puVar1 = DAT_005b9b00;
    uVar9 = FUN_0043de82(param_1);
    *puVar1 = uVar9;
    FUN_0043f4c0(*puVar1,200,0x120);
    FUN_0043f09a(*puVar1,param_2,0);
    uVar9 = FUN_0044104c(0);
    FUN_0044127e(*puVar1,uVar9,0);
    FUN_0044129e(*puVar1,0,0);
    FUN_0044131c(*puVar1,0,0);
    FUN_0044133a(*puVar1,0,0);
    FUN_00441378(*puVar1,0,0);
    FUN_00441386(*puVar1,0,0);
    FUN_005b8dd0(*puVar1,0,0);
    FUN_0044146a(*puVar1,0,0);
    uVar9 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar1,uVar9,0);
    FUN_0044142e(*puVar1,0xff,0);
    FUN_0043dfa4(*puVar1,0x10);
    service_time_current_calendar_get(auStack_4c);
    puVar4 = DAT_005b9c88;
    uVar9 = FUN_00499416(*puVar1);
    *puVar4 = uVar9;
    FUN_0043f506(*puVar4,0x3fffffff);
    FUN_0043f568(*puVar4,0x3fffffff);
    uVar9 = FUN_005b8e72(*DAT_005b9c78);
    FUN_0044143e(*puVar4,uVar9,0);
    FUN_0043c0e4(&local_68,8,0);
    FUN_004b4728(&local_68,DAT_005b9c8c,local_34,local_30);
    FUN_0049942e(*puVar4,&local_68);
    FUN_005b8e1a(*puVar4,6);
    *DAT_005b9c90 = local_34;
    *DAT_005b9c94 = local_30;
    puVar4 = DAT_005b9c98;
    pbVar3 = DAT_005b9c7c;
    if (*DAT_005b9c7c != 0) {
      uVar9 = FUN_00499416(*puVar1);
      *puVar4 = uVar9;
      FUN_0043f506(*puVar4,0x3fffffff);
      FUN_0043f568(*puVar4,0x3fffffff);
      FUN_0044143e(*puVar4,*DAT_005b9c48,0);
      FUN_0043c0e4(&local_60,0x10,0);
      iVar8 = DAT_005b9c9c;
      uVar9 = FUN_00460084(*(undefined4 *)(DAT_005b9c9c + local_48 * 4));
      uVar9 = FUN_0045fffe(*(undefined4 *)(iVar8 + local_48 * 4),uVar9);
      FUN_004b4728(&local_60,DAT_005b9ca0,uVar9,local_38);
      FUN_0049942e(*puVar4,&local_60);
      FUN_005b8e1a(*puVar4,0x2a);
    }
    *DAT_005b9ca4 = local_3c;
    *DAT_005b9ca8 = local_38;
    *DAT_005b9cac = local_48;
    puVar4 = DAT_005b9cb0;
    uVar9 = FUN_0043de82(*puVar1);
    *puVar4 = uVar9;
    FUN_0043f4c0(*puVar4,0x3fffffff,0x3fffffff);
    FUN_0044129e(*puVar4,0,0);
    FUN_0044131c(*puVar4,0,0);
    FUN_0044133a(*puVar4,0,0);
    FUN_00441386(*puVar4,0,0);
    FUN_005b8dd0(*puVar4,0,0);
    FUN_0044146a(*puVar4,0,0);
    uVar9 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar4,uVar9,0);
    FUN_0044142e(*puVar4,0xff,0);
    FUN_0043dfa4(*puVar4,0x10);
    FUN_0048ba78(*puVar4,0);
    FUN_0048ba92(*puVar4,0,2,2);
    FUN_00441254(*puVar4,0xc,0);
    puVar5 = DAT_005b9cb4;
    uVar9 = FUN_00498668(*puVar4);
    *puVar5 = uVar9;
    FUN_0043ded4(*puVar5,0x10000);
    FUN_0043dfa4(*puVar5,0x10);
    bVar6 = ui_common_api_fn_00509f8e();
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      local_60 = (uint)bVar6;
      local_64 = DAT_005b9cb8;
      local_68 = 0x1a7;
      FUN_0043d574(4,PTR_s_dashboard_wf_l2_005b9c70,PTR_s_D__01_workspace_s200_ap510b_iar__005b9c6c,
                   PTR_s_layout2_create_005b9c68);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005b9cbc,DAT_005b9cbc,bVar6);
    }
    uVar9 = FUN_005b8e84(bVar6);
    FUN_00498680(*puVar5,uVar9);
    iVar8 = FUN_0047d9c4();
    puVar5 = DAT_005b9cc0;
    if (iVar8 != 0) {
      uVar9 = FUN_00498668(*puVar4);
      *puVar5 = uVar9;
      FUN_0043ded4(*puVar5,0x10000);
      FUN_0043dfa4(*puVar5,0x10);
      iVar8 = FUN_0047d9cc();
      if (iVar8 == 0) {
        FUN_00498680(*puVar5,DAT_005b9cc4);
      }
      else {
        uVar7 = FUN_0049c5bc();
        uVar9 = FUN_005b8ece(uVar7);
        FUN_00498680(*puVar5,uVar9);
      }
    }
    if (*pbVar3 == 0) {
      uVar9 = 0x2a;
    }
    else {
      uVar9 = 0x48;
    }
    FUN_005b8e1a(*puVar4,uVar9);
    for (iVar8 = 0; puVar4 = DAT_005b9cc8, iVar8 < (int)(uint)*DAT_005b9c60; iVar8 = iVar8 + 1) {
      FUN_005b8f18(iVar8,local_50[iVar8]);
    }
    uVar9 = FUN_00498668(*puVar1);
    *puVar4 = uVar9;
    FUN_0043f506(*puVar4,0x3fffffff);
    FUN_0043f568(*puVar4,0x3fffffff);
    FUN_00498680(*puVar4,PTR_DAT_005b9ccc);
    FUN_0043ded4(*puVar4,0x10000);
    FUN_0043dfa4(*puVar4,0x10);
    uVar9 = FUN_005b8e4a(2);
    FUN_005b8e1a(*puVar4,uVar9);
    iVar8 = UX_GetSystemBLEStatus();
    if (iVar8 == 0) {
      for (iVar8 = 0; iVar2 = DAT_005b9c44, iVar8 < 3; iVar8 = iVar8 + 1) {
        if ((*(int *)(DAT_005b9c44 + iVar8 * 4) != 0) &&
           (iVar10 = FUN_0043e2ea(*(undefined4 *)(DAT_005b9c44 + iVar8 * 4)), iVar10 == 1)) {
          FUN_0043ded4(*(undefined4 *)(iVar2 + iVar8 * 4),1);
        }
      }
      FUN_0043dfa4(*puVar4,1);
    }
    else {
      for (iVar8 = 0; iVar2 = DAT_005b9c44, iVar8 < 3; iVar8 = iVar8 + 1) {
        if ((*(int *)(DAT_005b9c44 + iVar8 * 4) != 0) &&
           (iVar10 = FUN_0043e2ea(*(undefined4 *)(DAT_005b9c44 + iVar8 * 4)), iVar10 == 1)) {
          FUN_0043dfa4(*(undefined4 *)(iVar2 + iVar8 * 4),1);
        }
      }
      FUN_0043ded4(*puVar4,1);
    }
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      local_64 = PTR_s_layout2_created_at_x__d_005b9cd0;
      local_68 = 0x1e3;
      local_60 = param_2;
      FUN_0043d574(3,PTR_s_dashboard_wf_l2_005b9c70,PTR_s_D__01_workspace_s200_ap510b_iar__005b9c6c,
                   PTR_s_layout2_create_005b9c68);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashboard_wf_l2_layout2_created_005b9cd4,
                          PTR_s__dashboard_wf_l2_layout2_created_005b9cd4,param_2);
    }
    uVar9 = 0;
  }
  return uVar9;
}

