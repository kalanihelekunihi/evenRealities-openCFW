
undefined8 FUN_0053faba(uint param_1,int param_2)

{
  undefined4 uVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  uVar1 = DAT_0053ffec;
  if (param_2 == 1) {
    uVar2 = (uint)((param_1 & 7) == 0);
  }
  else if (param_2 == 2) {
    uVar2 = (uint)((param_1 & 3) == 0);
  }
  else if (param_2 == 4) {
    uVar2 = param_1 & 1 ^ 1;
  }
  else if (param_2 == 8) {
    uVar2 = 1;
  }
  else {
    FUN_0044d25c(3,DAT_0053fff4,0x50,DAT_0053fff0);
    uVar2 = 0;
    unaff_r7 = uVar1;
  }
  return CONCAT44(unaff_r7,uVar2);
}

