
undefined8
FUN_005d4040(int *param_1,undefined4 param_2,int *param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar1 = FT_MulFix(param_1[0xb5f],param_4,param_3,param_4,param_3,param_4);
  iVar2 = FT_MulFix(param_1[0xb60],param_5);
  iVar2 = iVar2 + iVar1;
  uVar3 = FUN_005d36f0(param_2,param_5);
  iVar1 = FT_MulFix(*(undefined4 *)(*param_1 + 0x40),iVar2);
  iVar4 = FT_MulFix(*(undefined4 *)(*param_1 + 0x48),uVar3);
  *param_3 = param_1[0xb62] + iVar4 + iVar1;
  iVar1 = FT_MulFix(*(undefined4 *)(*param_1 + 0x44),iVar2);
  iVar4 = FT_MulFix(*(undefined4 *)(*param_1 + 0x4c),uVar3);
  param_3[1] = param_1[0xb63] + iVar4 + iVar1;
  return CONCAT44(uVar3,iVar2);
}

