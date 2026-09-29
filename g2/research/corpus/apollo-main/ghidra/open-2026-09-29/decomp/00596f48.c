
undefined8 FUN_00596f48(undefined4 param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0xe7;
      FUN_0043d574(1,DAT_00597028,DAT_00597024,PTR_s_translate_action_result_00597094,0xe7,
                   PTR_s_translate_result_data_is_NULL_00597090);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__translate_fsm_translate_result_d_00597098,
                          PTR_s__translate_fsm_translate_result_d_00597098);
    }
    uVar2 = 0xffffffff;
  }
  else {
    translate_ui_0059e6d0();
    FUN_0059ec28(2,0);
    uVar2 = 0;
  }
  return CONCAT44(unaff_r5,uVar2);
}

