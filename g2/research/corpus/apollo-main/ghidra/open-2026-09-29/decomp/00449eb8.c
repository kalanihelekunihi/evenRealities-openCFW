
int * AllocBlock(int *param_1)

{
  int *piVar1;
  
  piVar1 = (int *)0x0;
  if (*param_1 != 0) {
    piVar1 = (int *)*param_1;
    *param_1 = *piVar1;
  }
  return piVar1;
}

