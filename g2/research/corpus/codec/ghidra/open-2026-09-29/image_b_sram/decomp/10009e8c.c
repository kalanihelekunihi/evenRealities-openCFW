
undefined4 FUN_10009e8c(uint param_1,int *param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (param_1 & 3) * 0xb00;
  iVar2 = DAT_10009ebc + 0x80;
  *(int *)(iVar1 + iVar2) = DAT_10009ebc;
  *(int *)(iVar2 + iVar1 + 0x10) = iVar1 + 0x20 + iVar2;
  *param_2 = iVar2 + iVar1;
  *param_3 = 0xb00;
  return 0;
}

