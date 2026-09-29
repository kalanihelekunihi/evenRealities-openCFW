
/* WARNING: Removing unreachable block (ram,0x10007de8) */

void FUN_10007d2c(uint *param_1,undefined4 *param_2)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  uVar4 = (*(ushort *)((int)param_1 + 6) & 0x3fff) >> 4;
  uVar6 = param_1[1];
  uVar7 = *param_1;
  uVar5 = uVar6 & 0x7ffff;
  param_2[1] = (uint)(*(byte *)((int)param_1 + 7) >> 7);
  if (uVar4 != 0) {
    if (uVar4 == 0x7ff) {
      if (uVar7 == 0 && uVar5 == 0) {
        *param_2 = 4;
      }
      else {
        *param_2 = 0;
        param_2[3] = uVar7 << 8;
        param_2[4] = (uVar6 & 0x7ffff) << 8 | uVar7 >> 0x18;
      }
    }
    else {
      param_2[2] = uVar4 - 0x3ff;
      *param_2 = 3;
      param_2[3] = uVar7 << 8;
      param_2[4] = uVar5 << 8 | uVar7 >> 0x18;
    }
    return;
  }
  if (uVar7 == 0 && uVar5 == 0) {
    *param_2 = 2;
    return;
  }
  uVar5 = uVar5 << 8 | uVar7 >> 0x18;
  uVar7 = uVar7 << 8;
  *param_2 = 3;
  iVar2 = -0x3ff;
  do {
    iVar3 = iVar2;
    bVar1 = CARRY4(uVar7,uVar7);
    uVar7 = uVar7 * 2;
    uVar5 = uVar5 * 2 + (uint)bVar1;
    iVar2 = iVar3 + -1;
  } while (uVar5 < 0x10000000);
  param_2[2] = iVar3;
  param_2[3] = uVar7;
  param_2[4] = uVar5;
  return;
}

