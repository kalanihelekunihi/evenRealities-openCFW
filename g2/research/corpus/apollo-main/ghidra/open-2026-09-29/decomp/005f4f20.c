
void Ins_SWAP(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = *param_1;
  *param_1 = param_1[1];
  param_1[1] = uVar1;
  return;
}

