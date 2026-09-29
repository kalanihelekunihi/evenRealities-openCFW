
undefined4 FT_Outline_Check(short *param_1)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if (param_1 != (short *)0x0) {
    iVar2 = (int)param_1[1];
    sVar1 = *param_1;
    if (sVar1 == 0 && param_1[1] == 0) {
      return 0;
    }
    if ((0 < iVar2) && (0 < sVar1)) {
      iVar3 = -1;
      for (iVar5 = 0; iVar5 < sVar1; iVar5 = iVar5 + 1) {
        iVar4 = (int)*(short *)(*(int *)(param_1 + 6) + iVar5 * 2);
        if (iVar4 <= iVar3) {
          return 6;
        }
        if (iVar2 <= iVar4) {
          return 6;
        }
        iVar3 = iVar4;
      }
      if (iVar3 == iVar2 + -1) {
        return 0;
      }
    }
  }
  return 6;
}

