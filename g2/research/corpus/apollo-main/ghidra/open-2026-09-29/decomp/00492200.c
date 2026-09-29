
ulonglong FUN_00492200(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4,
                      undefined2 param_5)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_004920aa(param_1,param_2);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    if ((*(short *)(param_2 + 0xc) == 0) || (*(int *)(param_2 + 8) != 0)) {
      FUN_00492114(param_1,*(undefined4 *)(param_2 + 8),*(undefined2 *)(param_2 + 0xc));
      FUN_00492198(param_1);
    }
    uVar2 = 1;
  }
  return (ulonglong)CONCAT24(param_5,uVar2);
}

