
bool case_initialize_serial_block(void)

{
  int iVar1;
  
  *DAT_08004f10 = *DAT_08004f10 | (int)DAT_08004f10 >> 0x16;
  iVar1 = case_initialize_interrupt_path(3);
  if (iVar1 == 0) {
    case_enable_interrupt_source();
  }
  return iVar1 != 0;
}

