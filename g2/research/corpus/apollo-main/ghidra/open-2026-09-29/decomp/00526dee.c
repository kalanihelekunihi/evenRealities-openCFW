
undefined4 FT_Set_Charmap(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  if (param_1 == 0) {
    uVar1 = 0x23;
  }
  else {
    piVar4 = *(int **)(param_1 + 0x28);
    if ((piVar4 == (int *)0x0) || (param_2 == 0)) {
      uVar1 = 0x26;
    }
    else {
      iVar2 = FT_Get_CMap_Format(param_2);
      if (iVar2 == 0xe) {
        uVar1 = 6;
      }
      else {
        piVar3 = piVar4 + *(int *)(param_1 + 0x24);
        for (; piVar4 < piVar3; piVar4 = piVar4 + 1) {
          if (*piVar4 == param_2) {
            *(int *)(param_1 + 0x5c) = *piVar4;
            return 0;
          }
        }
        uVar1 = 6;
      }
    }
  }
  return uVar1;
}

