
undefined4 Cy_SysClk_ClkHfSetDivider(uint param_1)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  
  uVar1 = DAT_00009f90;
  if (param_1 < 2) {
    uVar2 = Cy_SysClk_ClkHfGetDivider();
    if (param_1 == uVar2) {
      uVar1 = 0;
    }
    else if (((param_1 == 0) && (*(int *)(DAT_00009f94 + 0x30) < 0)) ||
            ((uVar1 = DAT_00009f98, param_1 == 1 &&
             (iVar3 = Cy_SysClk_ExtClkGetFrequency(), uVar1 = DAT_00009f98, iVar3 != 0)))) {
      *(uint *)(DAT_00009f94 + 0x28) = *(uint *)(DAT_00009f94 + 0x28) & 0xfffffffc | param_1 & 3;
      uVar1 = 0;
    }
  }
  return uVar1;
}

