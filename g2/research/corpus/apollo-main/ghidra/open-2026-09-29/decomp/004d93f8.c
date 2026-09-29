
undefined4 FUN_004d93f8(int *param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*(ushort *)(param_1 + 4) == param_2) {
    uVar2 = 1;
  }
  else if (*(ushort *)(*param_1 + 0x14) < param_2) {
    uVar2 = 0;
  }
  else {
    iVar1 = param_1[2];
    if (param_2 < *(ushort *)(param_1 + 4)) {
      *(undefined2 *)(param_1 + 2) = *(undefined2 *)(*param_1 + 0x10);
    }
    do {
      FUN_004d930a(param_1);
      if ((((*(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4) & 0xff) >> 2 ==
            (param_2 & 0x3f)) && (FUN_004d916e(param_1), *(ushort *)(param_1 + 4) == param_2)) &&
         ((*(byte *)((int)param_1 + 0x16) & 0xf) != 10)) {
        return 1;
      }
    } while ((short)param_1[2] != (short)iVar1);
    FUN_004d916e(param_1);
    uVar2 = 0;
  }
  return uVar2;
}

