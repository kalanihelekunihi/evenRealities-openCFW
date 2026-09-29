
void FUN_0043992c(uint *param_1,int param_2)

{
  int iVar1;
  undefined1 *puVar2;
  int iVar3;
  
  puVar2 = *(undefined1 **)(param_2 + 0xc);
  iVar1 = (int)puVar2 - *(int *)(param_2 + 8);
  if (iVar1 < 1) {
    iVar1 = 0;
  }
  iVar3 = (int)param_1[1] >> 3;
  if (iVar3 < iVar1) {
    iVar1 = iVar3;
  }
  param_1[1] = param_1[1] + iVar1 * -8;
  for (; iVar1 != 0; iVar1 = iVar1 + -1) {
    puVar2 = puVar2 + -1;
    *puVar2 = (char)*param_1;
    *param_1 = *param_1 >> 8;
  }
  if (7 < (int)param_1[1]) {
    param_1[1] = 0;
  }
  *(undefined1 **)(param_2 + 0xc) = puVar2;
  return;
}

