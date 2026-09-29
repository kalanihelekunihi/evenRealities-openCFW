
undefined4 FUN_004c2392(uint *param_1,uint *param_2,char param_3)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004c2adc)) {
    uVar1 = 2;
  }
  else {
    uVar2 = param_1[1];
    if (param_3 == '\0') {
      *param_2 = *(uint *)(DAT_004c26dc + uVar2 * 0x1000 + 0x204);
    }
    else {
      *param_2 = *(uint *)(DAT_004c26dc + uVar2 * 0x1000 + 0x204) &
                 *(uint *)(DAT_004c26dc + uVar2 * 0x1000 + 0x200);
    }
    uVar1 = 0;
  }
  return uVar1;
}

