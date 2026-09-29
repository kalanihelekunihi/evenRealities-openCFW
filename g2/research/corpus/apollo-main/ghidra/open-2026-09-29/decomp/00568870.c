
void FUN_00568870(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1[0xc];
  iVar1 = FT_Angle_Diff(*param_1,param_1[1],param_3,param_4,param_4);
  if (iVar1 == 0xb40000) {
    iVar1 = (int)(&DAT_005a0000 + param_2 * -0x2d0000) * -2;
  }
  FUN_0056851e(param_1 + param_2 * 8 + 0xd,param_1 + 2,iVar2,
               (int)(&DAT_005a0000 + param_2 * -0x2d0000) + *param_1,iVar1);
  *(undefined1 *)(param_1 + param_2 * 8 + 0x11) = 0;
  return;
}

