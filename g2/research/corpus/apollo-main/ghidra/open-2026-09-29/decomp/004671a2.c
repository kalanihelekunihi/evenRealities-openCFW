
undefined8 FUN_004671a2(int param_1,undefined *param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    iVar3 = 0x1d6;
    param_2 = PTR_s_advanced_setting_is_valid__kill__00467c2c;
    param_3 = param_1;
    FUN_0043d574(4,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                 PTR_s_setting_handle_advanced_setting_00467c30,0x1d6,
                 PTR_s_advanced_setting_is_valid__kill__00467c2c,param_1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004671ea;
  }
  compress_log_output(0x10400000,PTR_s__setting_advanced_setting_is_val_00467e50,
                      PTR_s__setting_advanced_setting_is_val_00467e50,param_1,iVar3,param_2,param_3)
  ;
LAB_004671ea:
  if ((param_1 == 1) && (cVar1 = FUN_0045a570(), cVar1 == '\x01')) {
    FUN_00464c36(0,0,0,0);
  }
  return CONCAT44(param_2,iVar3);
}

