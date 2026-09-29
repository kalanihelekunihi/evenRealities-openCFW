
int FUN_0059ba96(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = *(int *)(DAT_0059c178 + param_2 * 4) * (param_1 + 1);
  if (iVar1 < 0x21) {
    iVar2 = 0;
LAB_0059bace:
    iVar3 = 0;
LAB_0059bad0:
    iVar4 = 0;
LAB_0059bad2:
    iVar5 = 0;
  }
  else {
    iVar2 = 1;
    if (iVar1 < 0x41) goto LAB_0059bace;
    iVar3 = 1;
    if (iVar1 < 0x81) goto LAB_0059bad0;
    iVar4 = 1;
    if (iVar1 < 0x101) goto LAB_0059bad2;
    iVar5 = 1;
    if (0x200 < iVar1) {
      iVar1 = 1;
      goto LAB_0059bad6;
    }
  }
  iVar1 = 0;
LAB_0059bad6:
  return iVar2 + iVar3 + iVar4 + iVar5 + iVar1 + 4;
}

