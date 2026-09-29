
undefined4 als_function_23(undefined4 param_1,char param_2)

{
  undefined4 unaff_r7;
  
  *DAT_004ae8dc = param_1;
  *DAT_004ae8e0 = param_1;
  if (param_2 == '\0') {
    *DAT_004ae950 = 0;
  }
  else {
    *DAT_004ae950 = 1;
  }
  als_function_01(param_1,param_2);
  return unaff_r7;
}

