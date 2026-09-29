
void Move_CVT_Stretched(int param_1,int param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = Current_Ratio(param_1);
  iVar2 = FT_DivFix(param_3,uVar1);
  *(int *)(*(int *)(param_1 + 0x184) + param_2 * 4) =
       iVar2 + *(int *)(*(int *)(param_1 + 0x184) + param_2 * 4);
  return;
}

