
void case_release_peripheral(int *param_1)

{
  if (*param_1 == DAT_080062f8) {
    *DAT_080062fc = *DAT_080062fc & 0xffffbfff;
    case_release_pins(0x50000000,0x600);
    case_clear_irq(0x1b);
  }
  else if (*param_1 == DAT_08006300) {
    DAT_080062fc[-1] = DAT_080062fc[-1] & 0xfffbffff;
    case_release_pins(DAT_08006304,0x300);
    return;
  }
  return;
}

