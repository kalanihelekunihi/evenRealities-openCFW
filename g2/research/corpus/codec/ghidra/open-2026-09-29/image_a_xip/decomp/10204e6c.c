
undefined4 gx8002_aout_config_buffer(undefined4 param_1,uint *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = *param_2;
  if ((uVar1 == 0) || ((uVar1 & 0xf) != 0)) {
LAB_10204e76:
    uVar2 = 0xffffffff;
  }
  else {
    iRam00000004 = uVar1 + 0xe0000000;
    func_0x10025664(uVar1,param_2[2]);
    uVar1 = param_2[1];
    if (uVar1 != 0) {
      if ((uVar1 & 0xf) != 0) goto LAB_10204e76;
      iRam00000008 = uVar1 + 0xe0000000;
      func_0x10025664(uVar1,param_2[2]);
    }
    uRam0000000c = param_2[2];
    uVar2 = 0;
  }
  return uVar2;
}

