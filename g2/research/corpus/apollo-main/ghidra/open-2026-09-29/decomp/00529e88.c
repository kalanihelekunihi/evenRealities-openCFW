
void FUN_00529e88(undefined4 *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (param_2 == (undefined4 *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = *param_2;
  }
  *param_1 = uVar1;
  if (param_2 == (undefined4 *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = param_2[1];
  }
  param_1[1] = uVar1;
  return;
}

