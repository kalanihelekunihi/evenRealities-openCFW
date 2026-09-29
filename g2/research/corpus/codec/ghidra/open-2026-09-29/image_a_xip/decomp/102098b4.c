
/* WARNING: Removing unreachable block (ram,0x102098f8) */
/* WARNING: Removing unreachable block (ram,0x10209904) */
/* WARNING: Restarted to delay deadcode elimination for space: register */

undefined4 gx8002_div64(ulonglong *param_1,uint param_2)

{
  ulonglong uVar1;
  longlong lVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  
  uVar3 = *param_1;
  uVar7 = 0;
  if (*(uint *)((int)param_1 + 4) < param_2) {
    uVar8 = 0;
  }
  else {
    uVar8 = *(uint *)((int)param_1 + 4) / param_2;
    uVar3 = *param_1 - ((ulonglong)(param_2 * uVar8) << 0x20);
  }
  uVar4 = 1;
  while (((0 < (int)uVar7 ||
          ((uVar1 = (ulonglong)uVar8 << 0x20, uVar7 == 0 &&
           (uVar1 = (ulonglong)uVar8 << 0x20, param_2 != 0)))) &&
         (uVar1 = (ulonglong)uVar8 << 0x20, CONCAT44(uVar7,param_2) < uVar3))) {
    lVar2 = CONCAT44(uVar7,param_2) + CONCAT44(uVar7,param_2);
    param_2 = (uint)lVar2;
    uVar4 = uVar4 * 2;
    uVar7 = (uint)((ulonglong)lVar2 >> 0x20);
  }
  do {
    uVar8 = (uint)uVar4;
    if (CONCAT44(uVar7,param_2) <= uVar3) {
      uVar3 = uVar3 - CONCAT44(uVar7,param_2);
      uVar1 = uVar1 + uVar4;
    }
    uVar9 = uVar7 << 0x1f;
    uVar7 = uVar7 >> 1;
    param_2 = uVar9 | param_2 >> 1;
    uVar6 = uVar4 & 0x100000000;
    uVar5 = uVar4 >> 1;
    uVar4 = uVar4 >> 1;
  } while ((uVar6 != 0 || uVar8 >> 1 != 0) || (int)(uVar5 >> 0x20) != 0);
  *param_1 = uVar1;
  return (int)uVar3;
}

