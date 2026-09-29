
int FUN_004b28ee(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  int *piVar3;
  int iVar4;
  int local_24;
  int local_20;
  int local_1c;
  int local_18;
  undefined4 uStack_14;
  
  iVar1 = *(int *)(param_1 + 0x18);
  cVar2 = '\0';
  if ((*(ushort *)(iVar1 + 0x12) & 0x3fff) >> 0xd == 0) {
    piVar3 = *(int **)(iVar1 + 0xc);
    uStack_14 = param_4;
    if ((uint)piVar3[2] >> 0x1e == 0) {
      iVar4 = *piVar3;
      local_1c = param_2;
      local_18 = param_3;
      iVar1 = FUN_0052a284(&local_1c,iVar4,piVar3[2] & 0x3fffffff,2,&LAB_004b29a0_1);
      if (iVar1 != 0) {
        cVar2 = *(char *)(piVar3[1] + (iVar1 - iVar4 >> 1));
      }
    }
    else if ((uint)piVar3[2] >> 0x1e == 1) {
      iVar4 = *piVar3;
      local_24 = param_2;
      local_20 = param_3;
      iVar1 = FUN_0052a284(&local_24,iVar4,piVar3[2] & 0x3fffffff,4,&LAB_004b29b8_1);
      if (iVar1 != 0) {
        cVar2 = *(char *)(piVar3[1] + (iVar1 - iVar4 >> 2));
      }
    }
  }
  else {
    piVar3 = *(int **)(iVar1 + 0xc);
    if ((*(byte *)(piVar3[1] + param_2) != 0) && (*(byte *)(piVar3[2] + param_3) != 0)) {
      cVar2 = *(char *)(*piVar3 + (uint)*(byte *)((int)piVar3 + 0xd) *
                                  (*(byte *)(piVar3[1] + param_2) - 1) +
                                  (uint)*(byte *)(piVar3[2] + param_3) + -1);
    }
  }
  return (int)cVar2;
}

