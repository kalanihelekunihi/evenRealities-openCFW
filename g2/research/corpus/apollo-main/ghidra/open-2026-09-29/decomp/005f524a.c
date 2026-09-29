
void Ins_ROLL(undefined4 *param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = param_1[2];
  uVar2 = param_1[1];
  param_1[2] = *param_1;
  param_1[1] = uVar1;
  *param_1 = uVar2;
  return;
}

