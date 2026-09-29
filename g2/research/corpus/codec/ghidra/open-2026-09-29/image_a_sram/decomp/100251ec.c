
void gx_clock_set_module_snpu_enable(int param_1)

{
  gx8002_irq_save();
  if (param_1 == 0) {
    uRam00000018 = uRam00000018 | 0x100;
  }
  else {
    uRam00000018 = uRam00000018 & 0xfffffeff;
  }
  gx8002_irq_restore();
  return;
}

