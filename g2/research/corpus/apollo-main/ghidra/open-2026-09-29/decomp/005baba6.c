
undefined * FUN_005baba6(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  uint uVar3;
  
  uVar3 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar3 = 0xad;
    param_2 = PTR_s_layout4_pick_g_battery_dsc__leve_005bb2cc;
    FUN_0043d574(4,PTR_s_dashboard_wf_l4_005bb2d8,PTR_s_D__01_workspace_s200_ap510b_iar__005bb2d4,
                 PTR_s_layout4_pick_g_battery_dsc_005bb2d0,0xad,
                 PTR_s_layout4_pick_g_battery_dsc__leve_005bb2cc,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__dashboard_wf_l4_layout4_pick_g__005bb2dc,
                        PTR_s__dashboard_wf_l4_layout4_pick_g__005bb2dc,param_1 & 0xff,uVar3,param_2
                        ,param_3);
  }
  puVar2 = PTR_DAT_005bb2e0;
  if (((((param_1 & 0xff) != 0) && (puVar2 = PTR_DAT_005bb2e4, 0x14 < (param_1 & 0xff))) &&
      (puVar2 = PTR_DAT_005bb2e8, 0x28 < (param_1 & 0xff))) &&
     ((puVar2 = PTR_DAT_005bb2ec, 0x3c < (param_1 & 0xff) &&
      (puVar2 = PTR_DAT_005bb2f4, (param_1 & 0xff) < 0x51)))) {
    puVar2 = PTR_DAT_005bb2f0;
  }
  return puVar2;
}

