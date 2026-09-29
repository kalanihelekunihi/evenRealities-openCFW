
uint FUN_1000a85c(uint *param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  iVar1 = DAT_1000a894;
  uVar4 = 0;
  iVar3 = 0x20;
  do {
    uVar2 = 1 << (uVar4 & 0x3f);
    uVar4 = uVar4 + 1;
    if ((uVar2 & *(uint *)(DAT_1000a894 + 4)) == 0) {
      *param_1 = uVar4;
      *(uint *)(iVar1 + 4) = uVar2 | *(uint *)(iVar1 + 4);
      return *param_1;
    }
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return 0xffffffff;
}

