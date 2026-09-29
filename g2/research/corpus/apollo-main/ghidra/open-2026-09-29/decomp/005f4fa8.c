
void Ins_ODD(int param_1,uint *param_2)

{
  uint uVar1;
  
  uVar1 = (**(code **)(param_1 + 0x23c))(param_1,*param_2,0);
  *param_2 = (uint)((uVar1 & 0x7f) == 0x40);
  return;
}

