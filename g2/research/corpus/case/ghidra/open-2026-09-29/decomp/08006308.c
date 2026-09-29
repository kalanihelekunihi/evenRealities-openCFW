
void case_configure_resource_irq(int *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_4c;
  undefined4 local_2c;
  undefined4 uStack_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  
  FUN_080001e6(&local_2c,0x14);
  FUN_080001e6(&local_58,0x2c);
  iVar1 = DAT_080063e0;
  if (*param_1 == DAT_080063dc) {
    local_58 = 1;
    local_54 = 2;
    iVar2 = FUN_08005128(&local_58);
    if (iVar2 != 0) {
      case_fail_stop();
    }
    *(uint *)(DAT_080063e0 + 0x40) = *(uint *)(DAT_080063e0 + 0x40) | 0x4000;
    *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 1;
    local_24 = 0;
    local_18 = *(uint *)(iVar1 + 0x34) & 1;
    local_1c = 1;
    local_20 = 0;
    local_2c = 0x600;
    uStack_28 = 2;
    FUN_08004d30(0x50000000,&local_2c);
    case_forward_action(0x1b,3,0);
    case_interrupt_enable(0x1b);
  }
  else if (*param_1 == DAT_080063e4) {
    local_58 = 4;
    local_4c = 0;
    iVar2 = FUN_08005128(&local_58);
    if (iVar2 != 0) {
      case_fail_stop();
    }
    *(uint *)(iVar1 + 0x3c) = *(uint *)(iVar1 + 0x3c) | 0x40000;
    *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 2;
    local_24 = 0;
    local_18 = *(uint *)(iVar1 + 0x34) & 2;
    local_1c = 4;
    local_20 = 0;
    local_2c = 0x300;
    uStack_28 = 2;
    FUN_08004d30(DAT_080063e8,&local_2c);
  }
  return;
}

