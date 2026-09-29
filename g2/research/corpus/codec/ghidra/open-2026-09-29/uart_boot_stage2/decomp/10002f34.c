
undefined4 FUN_10002f34(int param_1,int param_2,undefined4 param_3,int param_4,undefined4 param_5)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = DAT_10002f94 + param_1 * 0x80;
  if ((param_2 == 0) || (param_4 == 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    *(int *)(iVar2 + 0x58) = param_4;
    *(undefined4 *)(iVar2 + 0x40) = 2;
    *(int *)(iVar2 + 0x60) = param_2;
    *(undefined4 *)(iVar2 + 100) = param_3;
    *(undefined4 *)(iVar2 + 0x5c) = param_5;
    *(undefined4 *)(iVar2 + 0x68) = 0xffffffff;
    if (*(int *)(iVar2 + 0x2c) != 0) {
      *(undefined4 *)(*(int *)(iVar2 + 4) + 0xa8) = 1;
      uVar1 = FUN_10003024(iVar2);
      return uVar1;
    }
    FUN_10003110();
    *(uint *)(*(int *)(iVar2 + 4) + 4) = *(uint *)(*(int *)(iVar2 + 4) + 4) | 1;
    FUN_1000311c();
    uVar1 = 0;
  }
  return uVar1;
}

