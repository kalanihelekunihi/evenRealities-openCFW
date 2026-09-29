
int * FUN_005d328a(int param_1,undefined4 *param_2,int *param_3,int *param_4)

{
  undefined4 uVar1;
  
  uVar1 = FT_DivFix(*(undefined4 *)(*(int *)(param_1 + 0x218) + 0x180),0x3e80000);
  *param_2 = uVar1;
  *param_3 = *(int *)(*(int *)(param_1 + 0x218) + 0x184) << 0x10;
  *param_4 = *(int *)(*(int *)(param_1 + 0x218) + 0x188) << 0x10;
  return param_4;
}

