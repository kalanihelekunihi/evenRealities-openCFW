
undefined4 gx8002_aout_set_channel(undefined4 param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  if (param_2 < 4) {
    uVar1 = (uint)*(byte *)(iRam10205088 + param_2);
    uVar2 = (uint)*(byte *)(iRam10205088 + 4 + param_2);
    uVar3 = (uint)*(byte *)(iRam10205088 + 8 + param_2);
  }
  else {
    uVar1 = 0;
    uVar2 = uVar1;
    uVar3 = uVar1;
  }
  uRam00000014 = uVar3 & 1 | (uVar2 & 7) << 0xc | (uVar1 & 0xf) << 8 | uRam00000014 & 0xffff00fe;
  return 0;
}

