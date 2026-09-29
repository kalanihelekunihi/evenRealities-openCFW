
void Ins_MUL(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = FT_MulDiv(*param_1,param_1[1],0x40);
  *param_1 = uVar1;
  return;
}

