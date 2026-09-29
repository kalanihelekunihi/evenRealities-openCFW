
ulonglong FUN_005446b8(undefined4 param_1,int param_2,int param_3,undefined1 *param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 *puStack_18;
  
  uVar1 = 0;
  puStack_18 = param_4;
  if (*(char *)(param_2 + 1) == '\x01') {
    iVar2 = 2;
    uVar1 = FUN_005858d8(param_1,*(undefined4 *)(param_2 + 4),&puStack_18,4,2,1);
    FUN_00543d0c(param_1,*(undefined4 *)(param_2 + 4),2);
    param_2 = iVar2;
  }
  else if (*(char *)(param_2 + 1) == '\x02') {
    if ((*(uint *)(param_2 + 0x10) < 0x58) || ((uint)(*(int *)(param_2 + 0x10) - param_3) < 0x58)) {
      iVar2 = 3;
      uVar1 = FUN_005858d8(param_1,*(undefined4 *)(param_2 + 4),&puStack_18,4,3,1);
      FUN_00543d0c(param_1,*(undefined4 *)(param_2 + 4),3);
      param_2 = iVar2;
      if (param_4 != (undefined1 *)0x0) {
        *param_4 = 1;
      }
    }
    else if (param_4 != (undefined1 *)0x0) {
      *param_4 = 0;
    }
  }
  return CONCAT44(param_2,uVar1) & 0xffffffff000000ff;
}

