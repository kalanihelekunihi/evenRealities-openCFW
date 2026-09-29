
undefined8 FUN_00415844(uint param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  if (param_2 == 0) {
    uVar3 = (param_1 >> 2) + (param_1 >> 1);
    uVar3 = uVar3 + (uVar3 >> 4);
    uVar3 = uVar3 + (uVar3 >> 8);
    uVar3 = uVar3 + (uVar3 >> 0x10) >> 3;
    iVar1 = uVar3 + (uVar3 * -10 + param_1 + 6 >> 4);
    iVar2 = 0;
  }
  else {
    uVar4 = (uint)((param_2 & 1) != 0) << 0x1f | param_1 >> 1;
    uVar3 = param_1 >> 2 | param_2 << 0x1e;
    uVar5 = uVar4 + uVar3;
    uVar6 = (param_2 >> 1) + (param_2 >> 2) + (uint)CARRY4(uVar4,uVar3);
    uVar3 = uVar5 >> 4 | uVar6 * 0x10000000;
    uVar4 = uVar5 + uVar3;
    uVar6 = uVar6 + (uVar6 >> 4) + (uint)CARRY4(uVar5,uVar3);
    uVar3 = uVar4 >> 8 | uVar6 * 0x1000000;
    uVar5 = uVar4 + uVar3;
    uVar6 = uVar6 + (uVar6 >> 8) + (uint)CARRY4(uVar4,uVar3);
    uVar3 = uVar5 >> 0x10 | uVar6 * 0x10000;
    uVar4 = uVar5 + uVar3;
    uVar3 = uVar6 + (uVar6 >> 0x10) + (uint)CARRY4(uVar5,uVar3);
    uVar6 = uVar3 + CARRY4(uVar4,uVar3);
    uVar5 = uVar4 + uVar3 >> 3 | uVar6 * 0x20000000;
    uVar6 = uVar6 >> 3;
    uVar4 = (uint)((ulonglong)uVar5 * 0xfffffff6);
    uVar3 = param_1 + uVar4;
    uVar4 = param_2 + ((uVar6 * -10 + (int)((ulonglong)uVar5 * 0xfffffff6 >> 0x20)) - uVar5) +
            (uint)CARRY4(param_1,uVar4) + (uint)(0xfffffff9 < uVar3);
    uVar3 = uVar3 + 6 >> 4 | uVar4 * 0x10000000;
    iVar1 = uVar5 + uVar3;
    iVar2 = (uVar4 >> 4) + uVar6 + (uint)CARRY4(uVar5,uVar3);
  }
  return CONCAT44(iVar2,iVar1);
}

