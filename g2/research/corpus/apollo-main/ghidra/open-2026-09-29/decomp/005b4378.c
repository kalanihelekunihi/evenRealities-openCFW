
undefined8 FUN_005b4378(int param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s_prep_note_list_is_NULL_005b48a0;
      local_10 = 0xf4;
      FUN_0043d574(1,DAT_005b485c,DAT_005b4858,PTR_s_conversate_prep_note_list_data_u_005b48a4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_data_prep_note_list_i_005b48a8,
                          PTR_s__conversate_data_prep_note_list_i_005b48a8);
    }
  }
  else {
    FUN_00439be4(DAT_005b48ac,param_1,0xaa8);
  }
  return CONCAT44(local_c,local_10);
}

