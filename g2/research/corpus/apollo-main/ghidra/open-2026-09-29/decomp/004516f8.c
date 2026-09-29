
bool FUN_004516f8(undefined4 *param_1,undefined4 *param_2)

{
  bool bVar1;
  
  if (param_1 == (undefined4 *)0x0) {
    param_1 = *(undefined4 **)*param_2;
  }
  else {
    param_1 = (undefined4 *)*param_1;
  }
  for (; (param_1 != (undefined4 *)0x0 && (param_1[3] == 0)); param_1 = (undefined4 *)*param_1) {
  }
  if (param_1 == (undefined4 *)0x0) {
    bVar1 = true;
  }
  else if (param_1[3] == 0) {
    bVar1 = true;
  }
  else {
    param_2[3] = 0;
    (*(code *)param_1[3])(param_1,param_2);
    bVar1 = -1 < (int)((uint)*(byte *)(param_2 + 6) << 0x1f);
  }
  return bVar1;
}

