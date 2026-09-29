
bool FUN_004488fc(int *param_1,int *param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  do {
    ExclusiveAccess(param_1);
    iVar3 = *param_1;
    if (iVar3 != *param_2) goto LAB_00448910;
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = param_3;
LAB_00448910:
  DataMemoryBarrier(0x1f);
  iVar2 = *param_2;
  if (iVar3 != iVar2) {
    *param_2 = iVar3;
  }
  return iVar3 == iVar2;
}

