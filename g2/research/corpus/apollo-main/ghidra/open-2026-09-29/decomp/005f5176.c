
void Ins_ROUND(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = (**(code **)(param_1 + 0x23c))
                    (param_1,*param_2,
                     *(undefined4 *)(param_1 + (uint)*(byte *)(param_1 + 0x174) * 4 + -0x94));
  *param_2 = uVar1;
  return;
}

