
undefined8 FUN_0048f77e(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_10;
  
  local_10 = param_4;
  iVar1 = FUN_0048f5ae(param_1,&local_10);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    FUN_00439c04(param_2,param_1,0x10);
    if (*(uint *)(param_2 + 8) < local_10) {
      uVar2 = DAT_0049011c;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar2 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar2;
      uVar2 = 0;
    }
    else {
      *(uint *)(param_2 + 8) = local_10;
      *(uint *)(param_1 + 8) = *(int *)(param_1 + 8) - local_10;
      uVar2 = 1;
    }
  }
  return CONCAT44(local_10,uVar2);
}

