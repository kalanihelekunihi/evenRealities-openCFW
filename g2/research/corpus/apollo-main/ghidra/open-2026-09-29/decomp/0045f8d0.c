
int FUN_0045f8d0(int *param_1)

{
  int iVar1;
  
  if (param_1 == (int *)0x0) {
    iVar1 = 0;
  }
  else if (*param_1 == 0) {
    iVar1 = param_1[1];
  }
  else {
    iVar1 = *param_1;
  }
  return iVar1;
}

