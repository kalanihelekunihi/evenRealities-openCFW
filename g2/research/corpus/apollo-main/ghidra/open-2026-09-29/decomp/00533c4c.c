
void attsIndCtrlCback(undefined2 *param_1)

{
  int iVar1;
  
  iVar1 = attsCcbByConnId((char)*param_1,0);
  if (iVar1 != 0) {
    attsIndNtfCallback((char)*param_1,iVar1,0);
  }
  return;
}

