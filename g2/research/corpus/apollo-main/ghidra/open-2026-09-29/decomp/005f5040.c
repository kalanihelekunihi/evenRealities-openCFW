
void Ins_DIV(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (param_2[1] == 0) {
    *(undefined4 *)(param_1 + 0xc) = 0x85;
  }
  else {
    uVar1 = FT_MulDiv_No_Round(*param_2,0x40,param_2[1]);
    *param_2 = uVar1;
  }
  return;
}

