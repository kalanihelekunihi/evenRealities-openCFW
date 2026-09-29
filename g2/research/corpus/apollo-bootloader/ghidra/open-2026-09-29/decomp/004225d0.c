
char * FUN_004225d0(uint *param_1,char param_2,uint param_3)

{
  uint *puVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  bool bVar5;
  bool bVar6;
  
  while (((uint)param_1 & 3) != 0) {
    bVar6 = param_3 == 0;
    param_3 = param_3 - 1;
    bVar5 = param_3 == 0;
    if (bVar6) goto LAB_00422620;
    puVar1 = (uint *)((int)param_1 + 1);
    uVar2 = *param_1;
    param_1 = puVar1;
    if (param_2 == (char)uVar2) goto LAB_00422624;
  }
  uVar2 = param_3 - 8;
  if (7 < param_3) {
    uVar2 = param_3 - 4;
    puVar1 = param_1;
    do {
      param_1 = puVar1;
      bVar5 = 3 < uVar2;
      uVar2 = uVar2 - 4;
      uVar4 = uVar2;
      if (bVar5) {
        uVar4 = *param_1 ^ CONCAT22(CONCAT11(param_2,param_2),CONCAT11(param_2,param_2));
        uVar4 = uVar4 + 0xfefefeff & ~uVar4 & 0x80808080;
      }
      puVar1 = param_1 + 1;
    } while (uVar4 == 0);
  }
  iVar3 = uVar2 + 8;
  puVar1 = param_1;
  do {
    param_1 = (uint *)((int)puVar1 + 1);
    bVar6 = iVar3 != 0;
    iVar3 = iVar3 + -1;
    bVar5 = iVar3 == 0;
    if (bVar6) {
      bVar5 = param_2 == (char)*puVar1;
    }
    puVar1 = param_1;
  } while (bVar6 && !bVar5);
LAB_00422620:
  puVar1 = param_1;
  if (!bVar5) {
    puVar1 = (uint *)0x1;
  }
LAB_00422624:
  return (char *)((int)puVar1 + -1);
}

