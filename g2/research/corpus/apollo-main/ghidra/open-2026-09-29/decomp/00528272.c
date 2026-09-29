
undefined4 ft_raccess_sort_ref_by_id(short *param_1,short *param_2)

{
  undefined4 uVar1;
  
  if (*param_1 < *param_2) {
    uVar1 = 0xffffffff;
  }
  else if (*param_2 < *param_1) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

