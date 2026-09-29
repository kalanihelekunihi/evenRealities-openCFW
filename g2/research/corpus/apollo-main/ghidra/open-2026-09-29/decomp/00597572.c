
undefined4 td_flag_set_with_reset(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == '\0') {
    *DAT_00597c34 = 0;
    td_temp_record_clear();
  }
  else {
    td_temp_record_invalidate();
  }
  return unaff_r7;
}

