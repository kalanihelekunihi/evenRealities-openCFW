
void LvpInitMaxKws(void)

{
  if (*(int *)(DAT_1020895c + 0x58) != 2) {
    gx8002_printf(PTR_s__LVP_MAX_DECODE___ERROR___The_ac_10208960);
  }
  KwsStrategyInit();
  return;
}

