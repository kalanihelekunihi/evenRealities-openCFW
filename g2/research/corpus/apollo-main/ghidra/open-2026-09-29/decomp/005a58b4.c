
undefined8 atScreenYHandler(void)

{
  uint uVar1;
  undefined4 unaff_r7;
  
  uVar1 = thunk_FUN_0048d86c();
  if (uVar1 < 0xc1) {
    FUN_0046c984();
    at_core_output(PTR_s_AT_SCRN_Y_OK_005a5968);
  }
  else {
    at_core_output(PTR_s_AT_SCRN_Y_Error_height_value_mus_005a5964);
  }
  return CONCAT44(unaff_r7,1);
}

