
int ui_onboarding_stock_sub_0050E468(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = ui_onboarding_stock_sub_0050CB28();
  param_1 = param_1 * 3;
  iVar3 = param_1 + 3;
  iVar2 = 0;
  for (; (param_1 < iVar3 && (param_1 < iVar1)); param_1 = param_1 + 1) {
    iVar2 = iVar2 + 1;
  }
  return iVar2;
}

