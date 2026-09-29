
int FUN_004cc200(int param_1,undefined4 *param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_004cac04(param_1,param_1 + 0x10,param_1,0,*param_2,param_2[1],param_3,param_4);
  if (iVar1 == 0) {
    uVar2 = FUN_00541af8(param_2[3],param_3,param_4);
    param_2[3] = uVar2;
    param_2[1] = param_4 + param_2[1];
    iVar1 = 0;
  }
  return iVar1;
}

