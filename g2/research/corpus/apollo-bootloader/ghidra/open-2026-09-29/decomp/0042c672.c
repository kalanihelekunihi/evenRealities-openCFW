
undefined4 hw_interrupt_status_get_42c672(uint *param_1,char param_2,uint *param_3)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0042cdb0)) {
    uVar1 = 2;
  }
  else if (param_3 == (uint *)0x0) {
    uVar1 = 6;
  }
  else {
    uVar2 = *(uint *)(DAT_0042c6e8 + param_1[1] * 0x1000 + 0x204);
    if (param_2 != '\0') {
      uVar2 = uVar2 & *(uint *)(DAT_0042c6e8 + param_1[1] * 0x1000 + 0x200);
    }
    *param_3 = uVar2;
    uVar1 = 0;
  }
  return uVar1;
}

