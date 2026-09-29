
void case_configure_irq_resource(int *param_1)

{
  uint *puVar1;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  uint local_c;
  
  FUN_080001e6(&local_20,0x14);
  if (*param_1 == DAT_08004708) {
    *DAT_0800470c = *DAT_0800470c | 0x100000;
    puVar1 = DAT_0800470c;
    DAT_0800470c[-3] = DAT_0800470c[-3] | 1;
    local_c = puVar1[-3] & 1;
    local_20 = 0x10;
    local_1c = 3;
    local_18 = 0;
    FUN_08004d30(0x50000000,&local_20);
    case_forward_action(0xc,3,0);
    case_interrupt_enable(0xc);
  }
  return;
}

