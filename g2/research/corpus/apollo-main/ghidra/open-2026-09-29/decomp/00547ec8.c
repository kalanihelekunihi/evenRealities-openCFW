
void FUN_00547ec8(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  byte bVar3;
  undefined1 uVar4;
  int iVar5;
  undefined4 in_r3;
  undefined4 uStack_70;
  undefined *puStack_6c;
  uint uStack_68;
  undefined4 uStack_60;
  undefined *puStack_50;
  undefined4 uStack_40;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    puStack_6c = PTR_s_Container_A_fade_out_complete__s_005485b0;
    uStack_70 = 0x582;
    FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                 PTR_s_navigation_container_A_fade_out__005485b4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_Container_A_fade_o_005485b8,
                        PTR_s__navigation_ui_Container_A_fade_o_005485b8);
  }
  puVar2 = DAT_00548558;
  FUN_0043dfa4(*DAT_00548558,1);
  FUN_00441488(*puVar2,0,0);
  puVar1 = DAT_00548554;
  FUN_0043ded4(*DAT_00548554,1);
  FUN_00440656(*puVar1);
  FUN_00440656(*puVar2);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    bVar3 = FUN_00545588(*puVar2,0);
    uStack_68 = (uint)bVar3;
    puStack_6c = PTR_s_Before_fade_in__Container_B_opac_005485bc;
    uStack_70 = 0x58e;
    FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                 PTR_s_navigation_container_A_fade_out__005485b4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    uVar4 = FUN_00545588(*puVar2,0);
    compress_log_output(0x10400000,PTR_s__navigation_ui_Before_fade_in__C_005485c0,
                        PTR_s__navigation_ui_Before_fade_in__C_005485c0,uVar4);
  }
  FUN_004503d6(&uStack_70);
  uStack_70 = *puVar2;
  puStack_6c = PTR_FUN_00547abc_1_00548598;
  FUN_004506ce(&uStack_70,0,0xff);
  uStack_40 = 100;
  puStack_50 = PTR_LAB_00450688_1_0054859c;
  uStack_60 = DAT_00548b40;
  FUN_00450408(&uStack_70);
  return;
}

