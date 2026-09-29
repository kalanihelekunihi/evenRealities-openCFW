
void FT_Outline_Translate(int param_1,int param_2,int param_3)

{
  ushort uVar1;
  int *piVar2;
  
  if (param_1 != 0) {
    piVar2 = *(int **)(param_1 + 4);
    for (uVar1 = 0; (int)(uint)uVar1 < (int)*(short *)(param_1 + 2); uVar1 = uVar1 + 1) {
      *piVar2 = param_2 + *piVar2;
      piVar2[1] = param_3 + piVar2[1];
      piVar2 = piVar2 + 2;
    }
  }
  return;
}

