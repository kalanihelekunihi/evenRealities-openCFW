
undefined8 FUN_004c0ea8(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004c0f68)) {
    iVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    if ((param_1[0x210] == 0) && (param_1[8] == 0)) {
      if (param_1[6] != 0) {
        iVar1 = FUN_004bfd62(param_1);
        if (iVar1 != 0) goto LAB_004c0f1c;
        FUN_004bfc86(param_1);
      }
      *param_1 = *param_1 & 0xfdffffff;
      if (*(int *)(DAT_004c0f5c + param_1[1] * 0x1000 + 0x90) << 0x1f < 0) {
        FUN_004807a0(param_1[0x233]);
      }
      iVar1 = 0;
    }
    else {
      iVar1 = 3;
    }
  }
  else {
    iVar1 = 0;
  }
LAB_004c0f1c:
  return CONCAT44(param_4,iVar1);
}

