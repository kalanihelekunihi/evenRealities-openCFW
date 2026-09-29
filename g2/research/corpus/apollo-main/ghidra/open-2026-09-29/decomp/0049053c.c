
undefined8 FUN_0049053c(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_10;
  
  local_10 = param_4;
  iVar1 = FUN_0048f5ae(param_1,&local_10);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else if (local_10 < 0x10000) {
    if (local_10 == 0) {
      FUN_0043c0e4(*(undefined4 *)(param_2 + 0x1c),*(undefined2 *)(param_2 + 0x12),0);
      uVar2 = 1;
    }
    else if (local_10 == *(ushort *)(param_2 + 0x12)) {
      uVar2 = FUN_0048f3be(param_1,*(undefined4 *)(param_2 + 0x1c),*(undefined2 *)(param_2 + 0x12));
    }
    else {
      uVar2 = DAT_004905dc;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar2 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar2;
      uVar2 = 0;
    }
  }
  else {
    uVar2 = DAT_004905cc;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar2 = 0;
  }
  return CONCAT44(local_10,uVar2);
}

