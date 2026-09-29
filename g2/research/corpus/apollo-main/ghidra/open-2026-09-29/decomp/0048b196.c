
uint * FUN_0048b196(uint *param_1,uint param_2,uint param_3,int param_4,uint param_5)

{
  uint uVar1;
  
  if (param_1 == (uint *)0x0) {
    param_1 = (uint *)0x0;
  }
  else {
    if ((param_2 & 0xff) == 0) {
      param_2 = *param_1 >> 8;
    }
    if (param_5 == 0) {
      param_5 = FUN_0048aad8(param_3,param_2 & 0xff);
    }
    uVar1 = FUN_0048b86c(param_3,param_4,param_2 & 0xff,param_5);
    if (param_1[3] < uVar1) {
      param_1 = (uint *)0x0;
    }
    else {
      *param_1 = *param_1 & 0xffff00ff | (param_2 & 0xff) << 8;
      param_1[1] = param_1[1] & 0xffff0000 | param_3 & 0xffff;
      param_1[1] = param_1[1] & 0xffff | param_4 << 0x10;
      param_1[2] = param_1[2] & 0xffff0000 | param_5 & 0xffff;
    }
  }
  return param_1;
}

