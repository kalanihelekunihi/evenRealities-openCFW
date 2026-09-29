
void FUN_004cfd84(int param_1,uint param_2)

{
  *(uint *)(param_1 + 4) = param_2 | *(uint *)(param_1 + 4) & (*DAT_004d0604 | *DAT_004d06d8);
  return;
}

