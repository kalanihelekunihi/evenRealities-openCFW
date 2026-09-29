
int FUN_0041595c(byte *param_1,int *param_2)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  bVar1 = false;
  iVar2 = 0;
  iVar3 = 0;
  if (*param_1 == 0x2d) {
    bVar1 = true;
    param_1 = param_1 + 1;
    iVar3 = 1;
  }
  for (; *param_1 - 0x30 < 10; param_1 = param_1 + 1) {
    iVar3 = iVar3 + 1;
    iVar2 = (*param_1 - 0x30) + iVar2 * 10;
  }
  if (param_2 != (int *)0x0) {
    *param_2 = iVar3;
  }
  if (bVar1) {
    iVar2 = -iVar2;
  }
  return iVar2;
}

