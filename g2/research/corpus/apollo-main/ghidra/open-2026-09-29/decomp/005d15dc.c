
void FUN_005d15dc(int param_1,int param_2,int param_3,char param_4)

{
  short sVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  int *piVar5;
  
  iVar4 = *(int *)(param_1 + 0x14);
  if (*(char *)(param_1 + 0x41) != '\0') {
    piVar5 = (int *)(*(int *)(iVar4 + 4) + *(short *)(iVar4 + 2) * 8);
    iVar2 = *(int *)(iVar4 + 8);
    sVar1 = *(short *)(iVar4 + 2);
    *piVar5 = param_2 >> 10;
    piVar5[1] = param_3 >> 10;
    if (param_4 == '\0') {
      uVar3 = 2;
    }
    else {
      uVar3 = 1;
    }
    *(undefined1 *)(iVar2 + sVar1) = uVar3;
  }
  *(short *)(iVar4 + 2) = *(short *)(iVar4 + 2) + 1;
  return;
}

