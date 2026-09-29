
void gx8002_clock_pll_wait(int *param_1)

{
  _clk_set_pll();
  if (*param_1 == 1) {
    do {
    } while ((*(uint *)(iRam1002507c + 0x18) & 8) == 0);
  }
  return;
}

