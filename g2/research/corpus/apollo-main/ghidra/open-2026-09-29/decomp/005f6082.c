
void Ins_SCANTYPE(int param_1,uint *param_2)

{
  if (-1 < (int)*param_2) {
    *(uint *)(param_1 + 0x158) = *param_2 & 0xffff;
  }
  return;
}

