
void dmPhyHciHandler(undefined2 *param_1)

{
  int iVar1;
  
  if (*(char *)(param_1 + 1) == '*') {
    dmPhyActDefPhySet(param_1);
  }
  else {
    iVar1 = dmConnCcbByHandle(*param_1);
    if (iVar1 != 0) {
      if (*(char *)(param_1 + 1) == ')') {
        dmPhyActPhyRead(iVar1,param_1);
      }
      else if (*(char *)(param_1 + 1) == '+') {
        dmPhyActPhyUpdate(iVar1,param_1);
      }
    }
  }
  return;
}

