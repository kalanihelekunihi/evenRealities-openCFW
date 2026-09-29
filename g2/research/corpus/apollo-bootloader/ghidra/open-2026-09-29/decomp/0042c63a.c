
undefined4 hw_interrupt_enable_42c63a(uint *param_1,uint param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0042cdb0)) {
    uVar1 = 2;
  }
  else if ((int)(param_2 << 0x1e) < 0) {
    uVar1 = 6;
  }
  else {
    *(uint *)(DAT_0042c6e8 + param_1[1] * 0x1000 + 0x200) =
         param_2 | *(uint *)(DAT_0042c6e8 + param_1[1] * 0x1000 + 0x200);
    uVar1 = 0;
  }
  return uVar1;
}

