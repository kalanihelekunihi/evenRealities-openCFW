
undefined4 LvpDoMaxDecoder(int param_1)

{
  int iVar1;
  
  iVar1 = gx8002_max_score(param_1,1);
  if ((iVar1 != 0) && (*(int *)(iRam1020893c + 0xb0) == 1)) {
    gx8002_max_score(param_1,0);
  }
  *(int *)(iRam10208940 + 4) = *(int *)(iRam10208940 + 4) + 1;
  iVar1 = gx8002_kws_strategy(param_1);
  if (iVar1 != 0) {
    *(undefined1 *)(param_1 + 0xd) = *(undefined1 *)(iVar1 + 4);
    gx8002_ctc_offset_clear();
    KwsStrategyReset();
  }
  return 0;
}

