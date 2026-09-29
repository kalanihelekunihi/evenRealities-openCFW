
undefined4 FUN_10002e28(uint param_1,undefined4 param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  
  if (1 < param_1) {
    return 0xffffffff;
  }
  FUN_10004a48((param_1 != 0) + '\x11',1);
  uVar1 = FUN_10004b50(0x10);
  uVar3 = uVar1 % 1000000;
  if (100 < uVar3) {
    if (100 < (int)(1000000 - uVar3)) goto LAB_10002e5e;
    uVar1 = uVar1 + 1000000;
  }
  uVar1 = uVar1 - uVar3;
LAB_10002e5e:
  iVar4 = param_1 * 0x80 + DAT_10002e8c;
  *(uint *)(iVar4 + 0xc) = uVar1;
  *(undefined4 *)(iVar4 + 0x10) = param_2;
  uVar2 = FUN_10002c38(iVar4);
  return uVar2;
}

