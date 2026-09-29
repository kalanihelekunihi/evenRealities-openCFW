
undefined4 cff_index_forget_element(undefined4 *param_1)

{
  undefined4 unaff_r7;
  
  if (param_1[8] == 0) {
    FT_Stream_ReleaseFrame(*param_1);
  }
  return unaff_r7;
}

