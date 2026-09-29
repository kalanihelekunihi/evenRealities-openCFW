
undefined8 FUN_005b4776(ushort param_1,undefined1 *param_2,ushort param_3)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  
  if ((param_2 == (undefined1 *)0x0) || (param_3 == 0)) {
    uVar3 = 0;
    uVar4 = 0;
  }
  else {
    *param_2 = 0;
    uVar4 = DAT_005b484c;
    if (param_1 < *(ushort *)(DAT_005b484c + 6)) {
      uVar1 = *(ushort *)(DAT_005b484c + (uint)param_1 * 2 + 10);
      uVar2 = *(ushort *)(DAT_005b484c + (uint)param_1 * 2 + 0xc);
      if ((uVar2 < uVar1) || (uVar4 = (uint)uVar2, *(ushort *)(DAT_005b484c + 4) < uVar4)) {
        uVar3 = 0;
      }
      else {
        while ((uVar1 < uVar2 &&
               ((*(char *)((uint)uVar2 + DAT_005b48c0 + -1) == '\n' ||
                (*(char *)(DAT_005b48c0 + (uint)uVar2 + -1) == '\r'))))) {
          uVar2 = uVar2 - 1;
        }
        uVar2 = uVar2 - uVar1;
        if (param_3 <= uVar2) {
          uVar2 = FUN_005b3ef8(DAT_005b48c0 + (uint)uVar1,param_3 - 1);
        }
        if (uVar2 != 0) {
          FUN_00439be4(param_2,DAT_005b48c0 + (uint)uVar1,uVar2);
        }
        uVar4 = (uint)uVar2;
        param_2[uVar4] = 0;
        uVar3 = (uint)uVar2;
      }
    }
    else {
      uVar3 = 0;
    }
  }
  return CONCAT44(uVar4,uVar3);
}

