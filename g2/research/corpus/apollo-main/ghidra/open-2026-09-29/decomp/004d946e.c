
undefined8
FUN_004d946e(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  undefined4 uVar2;
  
  if ((*(byte *)((int)param_1 + 0x16) & 0xf) == 10) {
    uVar2 = 1;
  }
  else {
    sVar1 = *(short *)(param_1 + 2);
    do {
      FUN_004d930a(param_1);
      if ((*(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4) & 0xfff) >> 8 ==
          10) {
        uVar2 = FUN_004d916e(param_1);
        goto LAB_004d94b6;
      }
    } while (*(short *)(param_1 + 2) != sVar1);
    FUN_004d916e(param_1);
    uVar2 = 0;
  }
LAB_004d94b6:
  return CONCAT44(param_4,uVar2);
}

