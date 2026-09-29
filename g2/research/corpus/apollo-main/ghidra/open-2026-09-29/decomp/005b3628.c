
bool FUN_005b3628(char *param_1,int param_2)

{
  bool bVar1;
  
  if ((param_1 == (char *)0x0) || (*param_1 == '\0')) {
    bVar1 = false;
  }
  else {
    bVar1 = -1 < param_2 - *(int *)(param_1 + 4);
  }
  return bVar1;
}

