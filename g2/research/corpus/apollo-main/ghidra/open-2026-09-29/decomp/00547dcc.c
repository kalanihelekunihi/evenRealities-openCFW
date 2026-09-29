
void FUN_00547dcc(void)

{
  int *piVar1;
  int iVar2;
  int local_68;
  undefined *local_64;
  undefined4 local_58;
  undefined *local_48;
  undefined4 local_38;
  
  piVar1 = DAT_00548558;
  if (((*DAT_00548550 == '\0') && (*DAT_00548554 != 0)) && (*DAT_00548558 != 0)) {
    *DAT_00548550 = '\x01';
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_64 = PTR_s_Starting_animation__hide_contain_005485a8;
      local_68 = 0x572;
      FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_hide_container_B_with_005485a4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_Starting_animatio_005485ac);
    }
    FUN_004503d6(&local_68);
    local_68 = *piVar1;
    local_64 = PTR_FUN_00547abc_1_00548598;
    FUN_004506ce(&local_68,0xff,0);
    local_38 = 100;
    local_48 = PTR_LAB_00450688_1_0054859c;
    local_58 = DAT_00548b3c;
    FUN_00450408(&local_68);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_64 = PTR_s_Animation_already_running_or_con_0054855c;
      local_68 = 0x56d;
      FUN_0043d574(2,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_hide_container_B_with_005485a4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__navigation_ui_Animation_already_00548564,
                          PTR_s__navigation_ui_Animation_already_00548564);
    }
  }
  return;
}

