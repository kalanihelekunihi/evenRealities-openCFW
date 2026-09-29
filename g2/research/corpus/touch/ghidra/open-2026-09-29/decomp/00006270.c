
uint touch_sub_2f70(int param_1,int param_2,int param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = __aeabi_uidiv(param_1 * param_3,100);
  uVar1 = uVar1 >> (param_4 & 0xff);
  uVar2 = (uint)(param_1 - param_2) >> (param_4 & 0xff);
  if (uVar1 <= uVar2) {
    uVar2 = uVar1;
  }
  return uVar2;
}

