
undefined8 FUN_00450a74(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  int *piVar3;
  bool bVar4;
  byte bVar5;
  
  uVar1 = DAT_00450b48;
  if ((param_1[1] == 0) && (param_1[2] == 0)) {
    uVar2 = 0;
  }
  else {
    bVar5 = 0;
    piVar3 = (int *)FUN_00482cd8(DAT_00450b48);
    while (piVar3 != (int *)0x0) {
      bVar4 = false;
      if (((piVar3 != param_1) &&
          (((-1 < piVar3[0xd] || ((*(byte *)(piVar3 + 0x17) & 0x1f) >> 4 != 0)) &&
           (*piVar3 == *param_1)))) && ((piVar3[1] != 0 && (piVar3[1] == param_1[1])))) {
        FUN_00482c0e(uVar1,piVar3);
        if (piVar3[5] != 0) {
          (*(code *)piVar3[5])(piVar3);
        }
        FUN_0044f758(piVar3);
        FUN_004509da();
        bVar5 = 1;
        bVar4 = true;
      }
      if (bVar4) {
        piVar3 = (int *)FUN_00482cd8(uVar1);
      }
      else {
        piVar3 = (int *)FUN_00482cf0(uVar1,piVar3);
      }
    }
    uVar2 = (uint)bVar5;
  }
  return CONCAT44(param_4,uVar2);
}

