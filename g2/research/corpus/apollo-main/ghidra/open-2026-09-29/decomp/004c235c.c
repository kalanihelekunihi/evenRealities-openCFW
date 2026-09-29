
undefined4 FUN_004c235c(uint *param_1,uint param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004c2adc)) {
    uVar1 = 2;
  }
  else {
    *(uint *)(DAT_004c26dc + param_1[1] * 0x1000 + 0x200) =
         *(uint *)(DAT_004c26dc + param_1[1] * 0x1000 + 0x200) & ~param_2;
    uVar1 = 0;
  }
  return uVar1;
}

