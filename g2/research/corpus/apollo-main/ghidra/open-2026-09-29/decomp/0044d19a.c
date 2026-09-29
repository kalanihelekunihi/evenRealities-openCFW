
bool FUN_0044d19a(undefined4 *param_1)

{
  bool bVar1;
  
  for (param_1 = (undefined4 *)*param_1;
      (param_1 != (undefined4 *)0x0 && ((*(byte *)(param_1 + 8) & 3) == 0));
      param_1 = (undefined4 *)*param_1) {
  }
  if (param_1 == (undefined4 *)0x0) {
    bVar1 = false;
  }
  else {
    bVar1 = (*(byte *)(param_1 + 8) & 3) == 1;
  }
  return bVar1;
}

