
int FUN_10007b50(uint param_1,undefined4 param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = (param_1 & 0x7fff) * (param_3 & 0x7fff);
  return ((uVar1 >> 0x10) +
         (param_3 >> 0x10) * (param_1 & 0x7fff) + (param_1 >> 0x10) * (param_3 & 0x7fff)) * 0x10000
         + (uVar1 & 0x7fff);
}

