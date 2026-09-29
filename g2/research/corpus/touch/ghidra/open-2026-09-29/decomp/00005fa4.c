
undefined4 pdl_timeout_count_scale(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  
  if (param_3 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = __aeabi_uidiv(param_2 * param_1);
  }
  return uVar1;
}

