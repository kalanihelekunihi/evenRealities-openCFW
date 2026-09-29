
undefined8
teleprompt_file_list_update
          (undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == (undefined2 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0xe;
      param_3 = DAT_0058bd88;
      FUN_0043d574(1,PTR_s_teleprompt_file_0058bd94,PTR_s_D__01_workspace_s200_ap510b_iar__0058bd90,
                   DAT_0058bd8c,0xe,DAT_0058bd88,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_file_file_list_is_NU_0058bd98,
                          PTR_s__teleprompt_file_file_list_is_NU_0058bd98);
    }
  }
  else {
    FUN_00439be4(DAT_0058bd9c,param_1,0xf52);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x13;
      param_3 = DAT_0058bda0;
      FUN_0043d574(4,PTR_s_teleprompt_file_0058bd94,PTR_s_D__01_workspace_s200_ap510b_iar__0058bd90,
                   DAT_0058bd8c,0x13,DAT_0058bda0,*param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0058bda4,DAT_0058bda4,*param_1);
    }
  }
  return CONCAT44(param_3,param_2);
}

