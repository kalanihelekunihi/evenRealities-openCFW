
void FT_Set_Transform(int param_1,int *param_2,int *param_3)

{
  int iVar1;
  int *piVar2;
  
  if (param_1 != 0) {
    piVar2 = *(int **)(param_1 + 0x80);
    piVar2[6] = 0;
    if (param_2 == (int *)0x0) {
      *piVar2 = 0x10000;
      piVar2[1] = 0;
      piVar2[2] = 0;
      piVar2[3] = 0x10000;
      param_2 = piVar2;
    }
    else {
      FUN_00439c04(piVar2,param_2,0x10);
    }
    if (((param_2[1] != 0 || param_2[2] != 0) || (*param_2 != 0x10000)) || (param_2[3] != 0x10000))
    {
      piVar2[6] = piVar2[6] | 1;
    }
    if (param_3 == (int *)0x0) {
      piVar2[4] = 0;
      piVar2[5] = 0;
      param_3 = piVar2 + 4;
    }
    else {
      iVar1 = param_3[1];
      piVar2[4] = *param_3;
      piVar2[5] = iVar1;
    }
    if (*param_3 != 0 || param_3[1] != 0) {
      piVar2[6] = piVar2[6] | 2;
    }
  }
  return;
}

