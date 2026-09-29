
void case_enable_interrupt_source(void)

{
  uint *puVar1;
  uint *puVar2;
  undefined4 in_r3;
  
  *DAT_08004fe8 = *DAT_08004fe8 | 1;
  puVar1 = DAT_08004fe8;
  puVar2 = DAT_08004fe8 + -0x10;
  DAT_08004fe8[-1] = DAT_08004fe8[-1] | (int)puVar2 * 0x10000;
  case_forward_action(0xfffffffe,3,0,in_r3,puVar1[-1] & (int)puVar2 * 0x10000);
  FUN_08005bc0(0x600);
  return;
}

