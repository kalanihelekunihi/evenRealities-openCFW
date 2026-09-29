
ulonglong FUN_0048b762(uint *param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = param_2[2] & 0xffff;
  uVar2 = FUN_0048aef8(param_1,param_2[1] & 0xffff,param_2[1] >> 0x10,*param_2 >> 8 & 0xff,uVar1,
                       param_2[4],param_2[3]);
  if ((uVar2 & 0xff) == 1) {
    *param_1 = *param_1 & 0xffff | *param_2 & 0xffff0000;
  }
  return CONCAT44(uVar1,uVar2) & 0xffffffff000000ff;
}

