
void FUN_004dfe50(int *param_1,char param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int local_70;
  undefined *local_6c;
  int local_68;
  undefined4 local_64;
  undefined4 local_60;
  int *local_54;
  undefined *local_50;
  undefined4 local_40;
  undefined4 local_38;
  undefined4 local_34;
  
  if (((param_1 != (int *)0x0) && (*param_1 != 0)) && (param_1[1] != 0)) {
    iVar1 = FUN_0043fce0(param_1[1]);
    if (iVar1 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_6c = PTR_s_Content_container_Y_not_zero_bef_004e031c;
        local_70 = 0x23e;
        local_68 = iVar1;
        FUN_0043d574(2,PTR_s_common_text_container_004dfff4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                     PTR_s_common_text_trigger_rubber_band_004e0320);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_Content_c_004e0324,
                            PTR_s__common_text_container_Content_c_004e0324,iVar1);
      }
      FUN_0043f142(param_1[1],0);
    }
    if (param_2 == '\0') {
      uVar3 = 0xfffffff0;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_64 = 0xfffffff0;
        local_68 = 0;
        local_6c = PTR_s_Triggering_BOTTOM_rubber_band__n_004e0330;
        local_70 = 0x24c;
        FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                     PTR_s_common_text_trigger_rubber_band_004e0320);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        local_70 = -0x10;
        compress_log_output(0x10800000,PTR_s__common_text_container_Triggerin_004e0334,
                            PTR_s__common_text_container_Triggerin_004e0334,0);
      }
    }
    else {
      uVar3 = 0x10;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_64 = 0x10;
        local_68 = 0;
        local_6c = PTR_s_Triggering_TOP_rubber_band__norm_004e0328;
        local_70 = 0x248;
        FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                     PTR_s_common_text_trigger_rubber_band_004e0320);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        local_70 = 0x10;
        compress_log_output(0x10800000,PTR_s__common_text_container_Triggerin_004e032c,
                            PTR_s__common_text_container_Triggerin_004e032c,0);
      }
    }
    FUN_004503d6(&local_70);
    local_70 = param_1[1];
    FUN_004506ce(&local_70,0,uVar3);
    local_40 = 100;
    local_6c = PTR_LAB_004dfcb8_1_004e0338;
    local_50 = PTR_LAB_00450672_1_004e02e8;
    local_34 = 100;
    local_38 = 0;
    local_60 = DAT_004e0b20;
    local_54 = param_1;
    FUN_00450408(&local_70);
    *(undefined1 *)((int)param_1 + 0x13) = 1;
  }
  return;
}

