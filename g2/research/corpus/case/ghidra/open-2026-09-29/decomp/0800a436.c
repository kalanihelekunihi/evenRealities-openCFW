
uint case_serial_read_byte(void)

{
  int iVar1;
  uint uVar2;
  byte bVar3;
  
  uVar2 = 0;
  bVar3 = 0;
  do {
    uVar2 = (uVar2 & 0x7f) * 2;
    case_write_selected_mask(1);
    case_delay_10();
    iVar1 = case_select_mask();
    if (iVar1 != 0) {
      uVar2 = uVar2 + 1;
    }
    case_write_selected_mask(0);
    case_delay_10();
    bVar3 = bVar3 + 1;
  } while (bVar3 < 8);
  return uVar2;
}

