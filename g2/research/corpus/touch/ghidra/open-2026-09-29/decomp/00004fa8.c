
uint touch_leaf_1ca8_median3(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = param_1;
  if (param_1 <= param_2) {
    uVar1 = param_2;
    param_2 = param_1;
  }
  if (uVar1 <= param_3) {
    param_3 = uVar1;
  }
  if (param_2 < param_3) {
    param_2 = param_3;
  }
  return param_2;
}

