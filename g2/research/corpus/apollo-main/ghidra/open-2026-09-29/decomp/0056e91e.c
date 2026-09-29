
void smpActPairCnfVerCalc1(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_2 + 4) + 9;
  FUN_00439be4(*(int *)(param_1 + 0x30) + 0x10,iVar1,0x10);
  smpCalcC1Part1(param_1,*(undefined4 *)(param_1 + 0x30),iVar1);
  return;
}

