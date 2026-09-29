
int FUN_00414b64(int *param_1,undefined4 param_2,undefined4 *param_3)

{
  int iVar1;
  undefined1 auStack_10 [8];
  
  iVar1 = *param_1;
  iVar1 = FUN_00410544(iVar1,iVar1 + 0x10,iVar1,*(undefined4 *)(*(int *)(iVar1 + 0x68) + 0x1c),
                       *param_3,param_3[1],auStack_10,8);
  if (iVar1 == 0) {
    FUN_00410b46(auStack_10);
    iVar1 = FUN_00410af2(auStack_10,param_1 + 1);
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      iVar1 = 1;
    }
  }
  return iVar1;
}

