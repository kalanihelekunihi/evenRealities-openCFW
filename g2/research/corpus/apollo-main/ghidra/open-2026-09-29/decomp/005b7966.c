
undefined * FUN_005b7966(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  uint uVar3;
  
  uVar3 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar3 = 0x9f;
    param_2 = PTR_s_layout1_pick_g_battery_dsc__leve_005b8494;
    FUN_0043d574(3,PTR_s_dashboard_wf_l1_005b84a0,PTR_s_D__01_workspace_s200_ap510b_iar__005b849c,
                 PTR_s_layout1_pick_g_battery_dsc_005b8498,0x9f,
                 PTR_s_layout1_pick_g_battery_dsc__leve_005b8494,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__dashboard_wf_l1_layout1_pick_g__005b84a4,
                        PTR_s__dashboard_wf_l1_layout1_pick_g__005b84a4,param_1 & 0xff,uVar3,param_2
                        ,param_3);
  }
  puVar2 = PTR_DAT_005b84a8;
  if (((((param_1 & 0xff) != 0) && (puVar2 = DAT_005b8564, 0x14 < (param_1 & 0xff))) &&
      (puVar2 = DAT_005b8568, 0x28 < (param_1 & 0xff))) &&
     ((puVar2 = DAT_005b858c, 0x3c < (param_1 & 0xff) &&
      (puVar2 = DAT_005b872c, (param_1 & 0xff) < 0x51)))) {
    puVar2 = DAT_005b8590;
  }
  return puVar2;
}

