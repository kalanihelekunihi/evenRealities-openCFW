
undefined8 FUN_00490150(undefined4 param_1,uint *param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_10;
  uint uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_0048f5b8(param_1,&local_10);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    if ((int)(local_10 << 0x1f) < 0) {
      *param_2 = ~((uint)((uStack_c & 1) != 0) << 0x1f | local_10 >> 1);
      param_2[1] = ~(uStack_c >> 1);
    }
    else {
      *param_2 = (uint)((uStack_c & 1) != 0) << 0x1f | local_10 >> 1;
      param_2[1] = uStack_c >> 1;
    }
    uVar2 = 1;
  }
  return CONCAT44(local_10,uVar2);
}

