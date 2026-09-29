
undefined4 FUN_005ba07c(int param_1,uint param_2,char *param_3)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  byte bVar4;
  undefined1 uVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  uint uVar9;
  uint local_a0;
  undefined *local_9c;
  uint local_98;
  uint local_94;
  uint local_90;
  undefined1 auStack_88 [4];
  int local_84;
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_70;
  undefined4 local_6c;
  undefined1 auStack_60 [64];
  
  if (param_1 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_9c = PTR_s_layout3_create__parent_NULL_005baaa8;
      local_a0 = 0x15c;
      FUN_0043d574(1,PTR_s_dashboard_wf_l3_005baab4,PTR_s_D__01_workspace_s200_ap510b_iar__005baab0,
                   PTR_s_layout3_create_005baaac);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__dashboard_wf_l3_layout3_create__005baab8,
                          PTR_s__dashboard_wf_l3_layout3_create__005baab8);
    }
    uVar7 = 0xffffffff;
  }
  else {
    if ((param_3 == (char *)0x0) || (*param_3 != '\x03')) {
      *DAT_005ba9d8 = 1;
      *DAT_005baabc = 1;
      *DAT_005baa98 = 1;
    }
    else {
      *DAT_005ba9d8 = param_3[4];
      *DAT_005baabc = param_3[5];
      *DAT_005baa98 = param_3[6];
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_90 = (uint)*DAT_005baa98;
      local_94 = (uint)*DAT_005baabc;
      local_98 = (uint)*DAT_005ba9d8;
      local_9c = DAT_005baac0;
      local_a0 = 0x16b;
      FUN_0043d574(3,PTR_s_dashboard_wf_l3_005baab4,PTR_s_D__01_workspace_s200_ap510b_iar__005baab0,
                   PTR_s_layout3_create_005baaac);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      local_9c = (undefined *)(uint)*DAT_005baa98;
      local_a0 = (uint)*DAT_005baabc;
      compress_log_output(0xcc00000,DAT_005baac4,DAT_005baac4,*DAT_005ba9d8);
    }
    iVar6 = UX_GetSystemBLEStatus();
    puVar2 = DAT_005baac8;
    uVar9 = (uint)(iVar6 != 0);
    uVar7 = FUN_0043de82(param_1);
    *puVar2 = uVar7;
    FUN_0043f4c0(*puVar2,200,0x120);
    FUN_0043f09a(*puVar2,param_2,0);
    uVar7 = FUN_0044104c(0);
    FUN_0044127e(*puVar2,uVar7,0);
    FUN_0044129e(*puVar2,0,0);
    FUN_0044131c(*puVar2,0,0);
    FUN_0044133a(*puVar2,0,0);
    FUN_00441378(*puVar2,0,0);
    FUN_00441386(*puVar2,0,0);
    FUN_005b9cec(*puVar2,0,0);
    FUN_0044146a(*puVar2,0,0);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar2,uVar7,0);
    FUN_0044142e(*puVar2,0xff,0);
    FUN_0043dfa4(*puVar2,0x10);
    service_time_current_calendar_get(auStack_88);
    puVar1 = DAT_005baacc;
    uVar7 = FUN_0043de82(*puVar2);
    *puVar1 = uVar7;
    FUN_0043f4c0(*puVar1,0x3fffffff,0x3fffffff);
    FUN_0044129e(*puVar1,0,0);
    FUN_0044131c(*puVar1,0,0);
    FUN_0044133a(*puVar1,0,0);
    FUN_00441386(*puVar1,0,0);
    FUN_005b9cec(*puVar1,0,0);
    FUN_0044146a(*puVar1,0,0);
    FUN_0043dfa4(*puVar1,0x10);
    puVar3 = DAT_005baad0;
    uVar7 = FUN_00498668(*puVar1);
    *puVar3 = uVar7;
    FUN_0043f506(*puVar3,0x1a);
    FUN_0043f568(*puVar3,0x1a);
    FUN_0043f09a(*puVar3,0,0);
    FUN_0043ded4(*puVar3,0x10000);
    FUN_0043dfa4(*puVar3,0x10);
    uVar7 = FUN_005b9dfa(local_70);
    FUN_00498680(*puVar3,uVar7);
    puVar3 = DAT_005baad4;
    uVar7 = FUN_00498668(*puVar1);
    *puVar3 = uVar7;
    FUN_0043f506(*puVar3,0x1a);
    FUN_0043f568(*puVar3,0x1a);
    FUN_0043f09a(*puVar3,0x20,0);
    FUN_0043ded4(*puVar3,0x10000);
    FUN_0043dfa4(*puVar3,0x10);
    uVar7 = FUN_005b9e7e(local_6c);
    FUN_00498680(*puVar3,uVar7);
    FUN_005b9d36(*puVar1,6);
    puVar1 = DAT_005baad8;
    uVar7 = FUN_00499416(*puVar2);
    *puVar1 = uVar7;
    FUN_0043f506(*puVar1,0x3fffffff);
    FUN_0043f568(*puVar1,0x3fffffff);
    uVar7 = DAT_005baadc;
    FUN_0044143e(*puVar1,DAT_005baadc,0);
    FUN_0043c0e4(&local_a0,8,0);
    FUN_005b9f06(local_70,local_6c,&local_a0,8);
    FUN_0049942e(*puVar1,&local_a0);
    FUN_005b9d36(*puVar1,0x28);
    *DAT_005baae0 = local_70;
    *DAT_005baae4 = local_6c;
    puVar1 = DAT_005baa9c;
    uVar8 = FUN_00498668(*puVar2);
    *puVar1 = uVar8;
    FUN_0043f506(*puVar1,0x3fffffff);
    FUN_0043f568(*puVar1,0x3fffffff);
    FUN_00498680(*puVar1,DAT_005baae8);
    FUN_0043ded4(*puVar1,0x10000);
    FUN_0043dfa4(*puVar1,0x10);
    FUN_005b9d36(*puVar1,0x40);
    puVar1 = DAT_005baaa4;
    if (*DAT_005baabc != 0) {
      uVar8 = FUN_00499416(*puVar2);
      *puVar1 = uVar8;
      FUN_0043f506(*puVar1,0x3fffffff);
      FUN_0043f568(*puVar1,0x3fffffff);
      FUN_0044143e(*puVar1,uVar7,0);
      FUN_0043c0e4(&local_98,0x10,0);
      iVar6 = DAT_005baaec;
      uVar8 = FUN_00460084(*(undefined4 *)(DAT_005baaec + local_84 * 4));
      uVar8 = FUN_0045fffe(*(undefined4 *)(iVar6 + local_84 * 4),uVar8);
      FUN_004b4728(&local_98,DAT_005baaf0,uVar8,local_74);
      FUN_0049942e(*puVar1,&local_98);
      uVar8 = FUN_0044104c(DAT_005baaf4);
      FUN_0044140e(*puVar1,uVar8,0);
      FUN_0044142e(*puVar1,0xff,0);
      FUN_005b9d36(*puVar1,0xe2);
    }
    *DAT_005baaf8 = local_78;
    *DAT_005baafc = local_74;
    *DAT_005bab00 = local_84;
    puVar1 = DAT_005baaa0;
    if (*DAT_005baa98 != 0) {
      uVar8 = FUN_00499416(*puVar2);
      *puVar1 = uVar8;
      FUN_0043f506(*puVar1,0x3fffffff);
      FUN_0043f568(*puVar1,0x3fffffff);
      FUN_0044143e(*puVar1,uVar7,0);
      FUN_0043c0e4(auStack_60,0x40,0);
      FUN_005b9f58(auStack_60,0x40);
      FUN_0049942e(*puVar1,auStack_60);
      uVar7 = FUN_0044104c(DAT_005baaf4);
      FUN_0044140e(*puVar1,uVar7,0);
      FUN_0044142e(*puVar1,0xff,0);
      FUN_005b9d36(*puVar1,0xf6);
    }
    puVar1 = DAT_005bab04;
    uVar7 = FUN_0043de82(*puVar2);
    *puVar1 = uVar7;
    FUN_0043f4c0(*puVar1,0x3fffffff,0x3fffffff);
    FUN_0044129e(*puVar1,0,0);
    FUN_0044131c(*puVar1,0,0);
    FUN_0044133a(*puVar1,0,0);
    FUN_00441386(*puVar1,0,0);
    FUN_005b9cec(*puVar1,0,0);
    FUN_0044146a(*puVar1,0,0);
    FUN_0043dfa4(*puVar1,0x10);
    FUN_0048ba78(*puVar1,0);
    FUN_0048ba92(*puVar1,0,2,2);
    FUN_00441254(*puVar1,0xc,0);
    puVar3 = DAT_005bab08;
    uVar7 = FUN_00498668(*puVar1);
    *puVar3 = uVar7;
    FUN_0043ded4(*puVar3,0x10000);
    FUN_0043dfa4(*puVar3,0x10);
    bVar4 = ui_common_api_fn_00509f8e();
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_98 = (uint)bVar4;
      local_9c = DAT_005bab0c;
      local_a0 = 0x1fa;
      FUN_0043d574(4,PTR_s_dashboard_wf_l3_005baab4,PTR_s_D__01_workspace_s200_ap510b_iar__005baab0,
                   PTR_s_layout3_create_005baaac);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005bab10,DAT_005bab10,bVar4);
    }
    uVar7 = FUN_005b9db0(bVar4);
    FUN_00498680(*puVar3,uVar7);
    iVar6 = FUN_0047d9c4();
    puVar3 = DAT_005bab14;
    if (iVar6 != 0) {
      uVar7 = FUN_00498668(*puVar1);
      *puVar3 = uVar7;
      FUN_0043ded4(*puVar3,0x10000);
      FUN_0043dfa4(*puVar3,0x10);
      iVar6 = FUN_0047d9cc();
      if (iVar6 == 0) {
        FUN_00498680(*puVar3,PTR_DAT_005bab18);
      }
      else {
        uVar5 = FUN_0049c5bc();
        uVar7 = FUN_005b9d66(uVar5);
        FUN_00498680(*puVar3,uVar7);
      }
    }
    FUN_0043f66c(*puVar2);
    iVar6 = FUN_0043fdda(*puVar1);
    FUN_005b9d36(*puVar1,0x11e - iVar6);
    FUN_005b9fd6(uVar9);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_9c = PTR_s_layout3_created_at_x__d__ble__d__005bab1c;
      local_a0 = 0x214;
      local_98 = param_2;
      local_94 = uVar9;
      FUN_0043d574(3,PTR_s_dashboard_wf_l3_005baab4,PTR_s_D__01_workspace_s200_ap510b_iar__005baab0,
                   PTR_s_layout3_create_005baaac);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      local_a0 = uVar9;
      compress_log_output(0xc800000,PTR_s__dashboard_wf_l3_layout3_created_005bab20,
                          PTR_s__dashboard_wf_l3_layout3_created_005bab20,param_2);
    }
    uVar7 = 0;
  }
  return uVar7;
}

