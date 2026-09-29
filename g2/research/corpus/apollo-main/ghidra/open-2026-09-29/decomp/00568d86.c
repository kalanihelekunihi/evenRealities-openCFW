
int FUN_00568d86(int *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  undefined4 uStack_20;
  
  iVar1 = 0;
  if ((param_1 == (int *)0x0) || (param_2 == (int *)0x0)) {
    iVar1 = 6;
  }
  else {
    local_30 = *param_2 - param_1[2];
    local_2c = param_2[1] - param_1[3];
    if ((local_30 != 0) || (local_2c != 0)) {
      uStack_20 = param_4;
      iVar2 = FT_Vector_Length(&local_30);
      iVar3 = FT_Atan2(local_30,local_2c);
      FT_Vector_From_Polar(&local_30,param_1[0xc],(int)&DAT_005a0000 + iVar3);
      if ((char)param_1[5] == '\0') {
        param_1[1] = iVar3;
        iVar1 = FUN_00568ce2(param_1,iVar2);
      }
      else {
        iVar1 = FUN_00568d2a(param_1,iVar3,iVar2);
      }
      if (iVar1 == 0) {
        piVar4 = param_1 + 0xd;
        for (iVar5 = 1; -1 < iVar5; iVar5 = iVar5 + -1) {
          local_28 = local_30 + *param_2;
          local_24 = local_2c + param_2[1];
          iVar1 = FUN_005683f2(piVar4,&local_28,1);
          if (iVar1 != 0) {
            return iVar1;
          }
          local_30 = -local_30;
          local_2c = -local_2c;
          piVar4 = piVar4 + 8;
          iVar1 = 0;
        }
        *param_1 = iVar3;
        iVar3 = param_2[1];
        param_1[2] = *param_2;
        param_1[3] = iVar3;
        param_1[4] = iVar2;
      }
    }
  }
  return iVar1;
}

