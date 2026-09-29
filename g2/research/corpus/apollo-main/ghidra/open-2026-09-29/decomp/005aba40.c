
undefined8 af_shaper_get_cluster(byte *param_1,int param_2,undefined4 *param_3,undefined4 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = 0;
  for (; *param_1 == 0x20; param_1 = param_1 + 1) {
  }
  uVar4 = (uint)*param_1;
  param_1 = param_1 + 1;
  if (0x7f < uVar4) {
    if (uVar4 < 0xe0) {
      iVar1 = 1;
      uVar4 = uVar4 & 0x1f;
    }
    else if (uVar4 < 0xf0) {
      iVar1 = 2;
      uVar4 = uVar4 & 0xf;
    }
    else {
      iVar1 = 3;
      uVar4 = uVar4 & 7;
    }
    for (; iVar1 != 0; iVar1 = iVar1 + -1) {
      uVar4 = *param_1 & 0x3f | uVar4 << 6;
      param_1 = param_1 + 1;
    }
  }
  while ((*param_1 != 0x20 && (*param_1 != 0))) {
    uVar3 = (uint)*param_1;
    param_1 = param_1 + 1;
    if (0x7f < uVar3) {
      if (uVar3 < 0xe0) {
        iVar1 = 1;
        uVar3 = uVar3 & 0x1f;
      }
      else if (uVar3 < 0xf0) {
        iVar1 = 2;
        uVar3 = uVar3 & 0xf;
      }
      else {
        iVar1 = 3;
        uVar3 = uVar3 & 7;
      }
      for (; iVar1 != 0; iVar1 = iVar1 + -1) {
        uVar3 = *param_1 & 0x3f | uVar3 << 6;
        param_1 = param_1 + 1;
      }
    }
  }
  if (uVar3 == 0) {
    uVar2 = FT_Get_Char_Index(**(undefined4 **)(param_2 + 0x24),uVar4);
    *param_3 = uVar2;
    *param_4 = 1;
  }
  else {
    *param_3 = 0;
    *param_4 = 0;
  }
  return CONCAT44(param_4,param_1);
}

