
uint gx8002_power_lock_create(uint *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  iVar1 = iRam102077a4;
  uVar3 = 0;
  iVar2 = 0x20;
  do {
    uVar4 = 1 << (uVar3 & 0x3f);
    uVar3 = uVar3 + 1;
    if ((*(uint *)(iRam102077a4 + 4) & uVar4) == 0) {
      *param_1 = uVar3;
      *(uint *)(iVar1 + 4) = *(uint *)(iVar1 + 4) | uVar4;
      return *param_1;
    }
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return 0xffffffff;
}

