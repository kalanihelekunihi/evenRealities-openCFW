
void Ins_SROUND(int param_1,undefined4 *param_2)

{
  SetSuperRound(param_1,0x4000,*param_2);
  *(undefined4 *)(param_1 + 0x13c) = 6;
  *(undefined4 *)(param_1 + 0x23c) = DAT_005f5b98;
  return;
}

