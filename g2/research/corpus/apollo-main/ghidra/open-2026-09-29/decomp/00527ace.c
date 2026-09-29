
void FT_Outline_Get_CBox(int param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;
  
  if ((param_1 != 0) && (param_2 != (int *)0x0)) {
    if (*(short *)(param_1 + 2) == 0) {
      iVar1 = 0;
      iVar2 = 0;
      iVar3 = 0;
      iVar4 = 0;
    }
    else {
      piVar5 = *(int **)(param_1 + 4);
      iVar1 = *piVar5;
      iVar2 = piVar5[1];
      iVar3 = iVar1;
      iVar4 = iVar2;
      piVar7 = piVar5;
      while (piVar6 = piVar7 + 2, piVar6 < piVar5 + *(short *)(param_1 + 2) * 2) {
        iVar8 = *piVar6;
        if (iVar8 < iVar1) {
          iVar1 = iVar8;
        }
        if (iVar3 < iVar8) {
          iVar3 = iVar8;
        }
        iVar8 = piVar7[3];
        if (iVar8 < iVar2) {
          iVar2 = iVar8;
        }
        piVar7 = piVar6;
        if (iVar4 < iVar8) {
          iVar4 = iVar8;
        }
      }
    }
    *param_2 = iVar1;
    param_2[2] = iVar3;
    param_2[1] = iVar2;
    param_2[3] = iVar4;
  }
  return;
}

