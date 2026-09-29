
undefined4 hw_interrupt_clear_42c6b6(uint *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0042cdb0)) {
    uVar1 = 2;
  }
  else {
    *(undefined4 *)(DAT_0042c6e8 + param_1[1] * 0x1000 + 0x208) = param_2;
    uVar1 = 0;
  }
  return uVar1;
}

