
void FUN_005d8828(int *param_1,int param_2,int param_3,uint *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  
  *param_4 = 0;
  iVar1 = param_1[0x208];
  iVar2 = *param_1;
  piVar4 = param_1 + 1;
  while( true ) {
    if ((iVar2 == 0) ||
       (iVar3 = param_2 - piVar4[3], iVar3 + param_1[0x207] < 0 != SCARRY4(iVar3,param_1[0x207])))
    goto LAB_005d8884;
    if (param_2 <= param_1[0x207] + piVar4[2]) break;
    iVar2 = iVar2 + -1;
    piVar4 = piVar4 + 8;
  }
  if (((char)iVar1 != '\0') || (iVar3 <= param_1[0x206])) {
    *param_4 = *param_4 | 1;
    param_4[1] = piVar4[4];
  }
LAB_005d8884:
  iVar2 = param_1[0x81];
  piVar4 = param_1 + 0x81 + iVar2 * 8 + -7;
  while( true ) {
    if (iVar2 == 0) {
      return;
    }
    iVar3 = piVar4[2] - param_3;
    if (iVar3 + param_1[0x207] < 0 != SCARRY4(iVar3,param_1[0x207])) break;
    if (piVar4[3] - param_1[0x207] <= param_3) {
      if (((char)iVar1 != '\0') || (iVar3 < param_1[0x206])) {
        *param_4 = *param_4 | 2;
        param_4[2] = piVar4[4];
      }
      return;
    }
    iVar2 = iVar2 + -1;
    piVar4 = piVar4 + -8;
  }
  return;
}

