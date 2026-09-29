
void Ins_S45ROUND(int param_1,undefined4 *param_2)

{
  SetSuperRound(param_1,0x2d41,*param_2);
  *(undefined4 *)(param_1 + 0x13c) = 7;
  *(undefined4 *)(param_1 + 0x23c) = DAT_005f5b9c;
  return;
}

