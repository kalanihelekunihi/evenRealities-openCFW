
void touch_pipeline_1cc2_median_shift(undefined4 param_1,undefined2 *param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  undefined2 uVar2;
  
  uVar1 = *param_3;
  uVar2 = touch_leaf_1ca8_median3(*param_2,uVar1,param_3[1]);
  param_3[1] = uVar1;
  *param_3 = *param_2;
  *param_2 = uVar2;
  return;
}

