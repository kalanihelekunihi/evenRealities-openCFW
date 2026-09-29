
int FUN_00529e52(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_2;
  uStack_c = param_4;
  iVar1 = FUN_004d4f90(*(undefined4 *)(*(int *)(param_1 + 0x34) + 0x1c),&local_10,param_1,param_4,
                       param_1,param_2);
  if (iVar1 == 0) {
    FUN_0044d25c(3,DAT_0052a20c,0xd1,DAT_0052a234,DAT_0052a230,param_2);
    iVar1 = 0;
  }
  return iVar1;
}

