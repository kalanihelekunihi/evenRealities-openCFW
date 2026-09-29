
int simplify_log_filename(int param_1,byte param_2,int param_3,int param_4)

{
  int iVar1;
  undefined *puStack_24;
  int iStack_20;
  uint uStack_1c;
  int iStack_18;
  
  if (((param_1 == 0) || (param_3 == 0)) || (param_4 == 0)) {
    iVar1 = 0;
  }
  else {
    iStack_18 = param_4;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_1c = (uint)param_2;
      puStack_24 = PTR_s_simple_change_log_filename__file_0045a53c;
      iStack_20 = param_1;
      FUN_0043d574(4,PTR_s_logger_setting_0045a4e8,PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                   PTR_s_simplify_log_filename_0045a540,0x21a);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__logger_setting_simple_change_lo_0045a544,
                          PTR_s__logger_setting_simple_change_lo_0045a544,param_1,param_2);
    }
    puStack_24 = (undefined *)0xffffffff;
    iVar1 = FUN_00475fc0(param_1,PTR_s_compress_log__d_bin_0045a548,&puStack_24);
    if (iVar1 == 1) {
      iVar1 = FUN_0044b728(param_3,param_4,PTR_s__c__d_0045a54c,param_2,puStack_24);
    }
    else {
      iVar1 = FUN_0046cacc(param_1,PTR_s_hardfault_txt_0045a550);
      if (iVar1 == 0) {
        iVar1 = FUN_0044b728(param_3,param_4,PTR_DAT_0045a554,param_2);
      }
    }
  }
  return iVar1;
}

