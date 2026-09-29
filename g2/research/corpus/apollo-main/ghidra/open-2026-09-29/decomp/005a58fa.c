
undefined4 atAlsHandler(void)

{
  int iVar1;
  
  iVar1 = thunk_FUN_0048d86c();
  if (iVar1 == 1) {
    als_function_28();
  }
  else if (iVar1 == 0) {
    als_function_29();
  }
  at_core_output(PTR_s_AT_ALS_OK_enable__d_005a5974,iVar1);
  return 1;
}

