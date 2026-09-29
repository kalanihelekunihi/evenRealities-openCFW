
undefined4 gx8002_flash_block_bounds(uint param_1,uint *param_2,uint *param_3)

{
  int *piVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  piVar1 = piRam100238e8;
  *param_3 = 0;
  *param_2 = 0;
  if (*piVar1 < 0) {
LAB_100238c6:
    uVar2 = 0xffffffff;
  }
  else {
    uVar4 = 0;
    do {
      uVar3 = uVar4;
      if (uVar3 == (piVar1[1] & 0xfffff000U)) goto LAB_100238c6;
      uVar4 = uVar3 + 0x1000;
    } while ((param_1 < uVar3) || (uVar4 <= param_1));
    *param_2 = uVar3;
    uVar2 = 0;
    *param_3 = uVar4;
  }
  return uVar2;
}

