
void case_configure_controller_irq(int *param_1)

{
  int iVar1;
  undefined4 local_38 [9];
  undefined4 local_14;
  uint local_c;
  
  FUN_080001e6(local_38,0x2c);
  if (*param_1 == DAT_08005b84) {
    local_38[0] = 0x20000;
    local_14 = 0x200;
    iVar1 = FUN_08005128(local_38);
    if (iVar1 != 0) {
      case_fail_stop();
    }
    *(uint *)(DAT_08005b88 + 0x1c) = *(uint *)(DAT_08005b88 + 0x1c) | 0x8000;
    iVar1 = DAT_08005b88;
    local_c = DAT_08005b88 + -0x40 >> 0x14;
    *(uint *)(DAT_08005b88 + -4) = *(uint *)(DAT_08005b88 + -4) | local_c;
    local_c = *(uint *)(iVar1 + -4) & local_c;
    case_forward_action(2,3,0);
    case_interrupt_enable(2);
  }
  return;
}

