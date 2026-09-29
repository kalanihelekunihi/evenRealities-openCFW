
undefined8
common_exit_prompt_fade_cb_step1
          (undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x3d;
    param_3 = PTR_s_step_1_0058c100;
    FUN_0043d574(3,PTR_s_exit_prompt_0058c0c4,PTR_s_D__01_workspace_s200_ap510b_iar__0058c0c0,
                 PTR_s_common_exit_prompt_fade_cb_step1_0058c104,0x3d,PTR_s_step_1_0058c100,param_4)
    ;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__exit_prompt_step_1_0058c108,
                        PTR_s__exit_prompt_step_1_0058c108);
  }
  puVar1 = DAT_0058c0dc;
  FUN_0044d878(*DAT_0058c0dc);
  uVar3 = FUN_00499416(*puVar1);
  FUN_0043f4c0(uVar3,0x3fffffff);
  FUN_0043f6b8(uVar3,9,0,0);
  FUN_0049942e(uVar3,*DAT_0058c0e0);
  FUN_0044143e(uVar3,*DAT_0058c10c,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar3,uVar4,0);
  FUN_0044145a(uVar3,2,0);
  FUN_0058c238(*puVar1,0xfa,PTR_common_exit_prompt_fade_cb_step2_1_0058c110);
  return CONCAT44(param_3,param_2);
}

