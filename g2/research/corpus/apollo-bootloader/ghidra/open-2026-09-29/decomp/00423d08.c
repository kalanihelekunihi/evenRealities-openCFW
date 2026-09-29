
longlong qsort_public_wrapper(int param_1,uint param_2,int param_3,int param_4)

{
  undefined4 local_10;
  
  if (param_1 == 0) {
    return (ulonglong)param_2 << 0x20;
  }
  local_10 = param_3;
  if (param_4 != 0) {
    qsort_introsort_core(param_1,param_2,param_2,param_3);
    local_10 = param_4;
  }
  return CONCAT44(param_4,local_10);
}

