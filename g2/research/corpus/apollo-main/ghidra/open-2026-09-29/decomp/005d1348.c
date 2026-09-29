
void FUN_005d1348(int param_1,undefined4 param_2,undefined4 param_3,char param_4)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  
  iVar5 = *(int *)(param_1 + 0x14);
  if (*(char *)(param_1 + 0x41) != '\0') {
    piVar6 = (int *)(*(int *)(iVar5 + 4) + *(short *)(iVar5 + 2) * 8);
    iVar3 = *(int *)(iVar5 + 8);
    sVar1 = *(short *)(iVar5 + 2);
    iVar4 = FT_RoundFix(param_2);
    *piVar6 = iVar4 >> 0x10;
    iVar4 = FT_RoundFix(param_3);
    piVar6[1] = iVar4 >> 0x10;
    if (param_4 == '\0') {
      uVar2 = 2;
    }
    else {
      uVar2 = 1;
    }
    *(undefined1 *)(iVar3 + sVar1) = uVar2;
  }
  *(short *)(iVar5 + 2) = *(short *)(iVar5 + 2) + 1;
  return;
}

