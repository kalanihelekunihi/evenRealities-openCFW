
undefined4 FUN_004d2112(byte *param_1,byte param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  bool bVar4;
  
  uVar2 = (uint)param_2;
  while( true ) {
    while( true ) {
      if (param_3 < 3) {
        while( true ) {
          if (param_3 == 0) {
            return 0;
          }
          if (*param_1 == uVar2) break;
          param_3 = param_3 - 1;
          param_1 = param_1 + 1;
        }
        return 1;
      }
      if (param_1[1] == 0x2d) break;
      if (*param_1 == uVar2) {
        return 1;
      }
      param_3 = param_3 - 1;
      param_1 = param_1 + 1;
    }
    uVar3 = (uint)*param_1;
    bVar4 = SBORROW4(uVar2,uVar3);
    iVar1 = uVar2 - uVar3;
    if (uVar3 <= uVar2) {
      bVar4 = SBORROW4((uint)param_1[2],uVar2);
      iVar1 = param_1[2] - uVar2;
    }
    if (iVar1 < 0 == bVar4) break;
    param_1 = param_1 + 3;
    param_3 = param_3 - 3;
  }
  return 1;
}

