
uint FUN_0055bce8(uint param_1,int param_2,uint param_3,undefined4 param_4,int param_5,
                 undefined4 param_6,uint param_7,int param_8)

{
  uint uVar1;
  
  uVar1 = (param_1 & 3) << 0x14 | DAT_0055c514 & param_8 << 8;
  if (param_2 == 1) {
    uVar1 = uVar1 | 2;
  }
  else {
    uVar1 = uVar1 | 1;
  }
  return uVar1 | (param_3 & 1) << 7 | param_5 << 0x18 | (param_7 & 7) << 4;
}

