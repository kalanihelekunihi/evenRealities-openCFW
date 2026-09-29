
ulonglong FUN_0048b134(undefined4 param_1,uint *param_2)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = param_2[2];
  puVar1 = (uint *)FUN_0048b010(param_1,param_2[1] & 0xffff,param_2[1] >> 0x10,*param_2 >> 8 & 0xff)
  ;
  if (puVar1 == (uint *)0x0) {
    puVar1 = (uint *)0x0;
  }
  else {
    *puVar1 = *puVar1 & 0xffff | *param_2 & 0xffff0000;
    *puVar1 = *puVar1 & 0xffff | (*puVar1 >> 0x10 | 0x30) << 0x10;
    if (param_2[3] < puVar1[3]) {
      uVar3 = param_2[3];
    }
    else {
      uVar3 = puVar1[3];
    }
    FUN_00454738(puVar1[4],param_2[4],uVar3);
  }
  return CONCAT44(uVar2,puVar1) & 0xffffffffffff;
}

