
void Ins_SDS(int param_1,uint *param_2)

{
  if (*param_2 < 7) {
    *(short *)(param_1 + 0x152) = (short)*param_2;
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 0x84;
  }
  return;
}

