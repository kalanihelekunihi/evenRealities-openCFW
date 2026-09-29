
void FUN_00547ad2(void)

{
  byte *pbVar1;
  int *piVar2;
  int *piVar3;
  byte bVar4;
  undefined1 uVar5;
  int iVar6;
  uint uVar7;
  int local_70;
  undefined *local_6c;
  uint local_68;
  int local_64;
  undefined *local_60;
  undefined *local_50;
  undefined4 local_40;
  
  piVar3 = DAT_00548558;
  piVar2 = DAT_00548554;
  pbVar1 = DAT_00548550;
  if (((*DAT_00548550 == 0) && (*DAT_00548554 != 0)) && (*DAT_00548558 != 0)) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_6c = PTR_s_Starting_animation__show_contain_00548570;
      local_70 = 0x552;
      FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_show_container_B_with_00548560);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_Starting_animatio_00548574,
                          PTR_s__navigation_ui_Starting_animatio_00548574);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      uVar7 = FUN_0043e0e0(*piVar2,1);
      local_68 = (uVar7 ^ 1) & 0xff;
      local_6c = PTR_s_Container_A_visible___d_00548578;
      local_70 = 0x553;
      FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_show_container_B_with_00548560);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      bVar4 = FUN_0043e0e0(*piVar2,1);
      compress_log_output(0x10400000,PTR_s__navigation_ui_Container_A_visib_0054857c,
                          PTR_s__navigation_ui_Container_A_visib_0054857c,bVar4 ^ 1);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      uVar7 = FUN_0043e0e0(*piVar3,1);
      local_68 = (uVar7 ^ 1) & 0xff;
      local_6c = PTR_s_Container_B_visible___d_00548580;
      local_70 = 0x554;
      FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_show_container_B_with_00548560);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      bVar4 = FUN_0043e0e0(*piVar3,1);
      compress_log_output(0x10400000,PTR_s__navigation_ui_Container_B_visib_00548584,
                          PTR_s__navigation_ui_Container_B_visib_00548584,bVar4 ^ 1);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      bVar4 = FUN_00545588(*piVar2,0);
      local_68 = (uint)bVar4;
      local_6c = PTR_s_Container_A_opacity___d_00548588;
      local_70 = 0x555;
      FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_show_container_B_with_00548560);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      uVar5 = FUN_00545588(*piVar2,0);
      compress_log_output(0x10400000,PTR_s__navigation_ui_Container_A_opaci_0054858c,
                          PTR_s__navigation_ui_Container_A_opaci_0054858c,uVar5);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      bVar4 = FUN_00545588(*piVar3,0);
      local_68 = (uint)bVar4;
      local_6c = PTR_s_Container_B_opacity___d_00548590;
      local_70 = 0x556;
      FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_show_container_B_with_00548560);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      uVar5 = FUN_00545588(*piVar3,0);
      compress_log_output(0x10400000,PTR_s__navigation_ui_Container_B_opaci_00548594,
                          PTR_s__navigation_ui_Container_B_opaci_00548594,uVar5);
    }
    FUN_00441488(*piVar2,0xff,0);
    FUN_00440656(*piVar2);
    *pbVar1 = 1;
    FUN_004503d6(&local_70);
    local_70 = *piVar2;
    local_6c = PTR_FUN_00547abc_1_00548598;
    FUN_004506ce(&local_70,0xff,0);
    local_40 = 100;
    local_50 = PTR_LAB_00450688_1_0054859c;
    local_60 = PTR_FUN_00547ec8_1_005485a0;
    FUN_00450408(&local_70);
  }
  else {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_6c = PTR_s_Animation_already_running_or_con_0054855c;
      local_70 = 0x54b;
      FUN_0043d574(2,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_show_container_B_with_00548560);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__navigation_ui_Animation_already_00548564,
                          PTR_s__navigation_ui_Animation_already_00548564);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_60 = (undefined *)*DAT_00548558;
      local_64 = *DAT_00548554;
      local_68 = (uint)*pbVar1;
      local_6c = PTR_s_animation_running__d__mini_map___00548568;
      local_70 = 0x54d;
      FUN_0043d574(2,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                   PTR_s_navigation_show_container_B_with_00548560);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      local_6c = (undefined *)*DAT_00548558;
      local_70 = *DAT_00548554;
      compress_log_output(0x8c00000,PTR_s__navigation_ui_animation_running_0054856c,
                          PTR_s__navigation_ui_animation_running_0054856c,*pbVar1);
    }
  }
  return;
}

