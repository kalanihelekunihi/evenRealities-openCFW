
void touch_record_1b60_replicate3(undefined4 param_1,undefined2 *param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  
  uVar1 = *param_2;
  *param_3 = uVar1;
  param_3[1] = uVar1;
  param_3[2] = *param_2;
  return;
}

