
/* WARNING: Removing unreachable block (ram,0x1000c622) */
/* WARNING: Removing unreachable block (ram,0x1000c632) */
/* WARNING: Removing unreachable block (ram,0x1000c686) */
/* WARNING: Restarted to delay deadcode elimination for space: register */

undefined4 FUN_1000c5d0(ulonglong *param_1,uint param_2)

{
  ulonglong uVar1;
  ulonglong uVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar3 = *param_1;
  uVar5 = 0;
  if (*(uint *)((int)param_1 + 4) < param_2) {
    uVar6 = 0;
  }
  else {
    uVar6 = *(uint *)((int)param_1 + 4) / param_2;
    uVar3 = *param_1 - ((ulonglong)(param_2 * uVar6) << 0x20);
  }
  if ((param_2 == 0) || (((int)(uVar3 >> 0x20) == 0 && ((uint)uVar3 <= param_2)))) {
    uVar4 = 1;
    uVar2 = (ulonglong)uVar6 << 0x20;
  }
  else {
    uVar4 = 1;
    do {
      uVar1 = CONCAT44(uVar5,param_2) + CONCAT44(uVar5,param_2);
      param_2 = (uint)uVar1;
      uVar5 = (uint)(uVar1 >> 0x20);
      uVar4 = uVar4 * 2;
      uVar2 = (ulonglong)uVar6 << 0x20;
      if ((longlong)uVar1 < 1) break;
      uVar2 = (ulonglong)uVar6 << 0x20;
    } while (uVar1 < uVar3);
  }
  do {
    if (CONCAT44(uVar5,param_2) <= uVar3) {
      uVar3 = uVar3 - CONCAT44(uVar5,param_2);
      uVar2 = uVar2 + uVar4;
    }
    uVar6 = uVar5 << 0x1f;
    uVar5 = uVar5 >> 1;
    param_2 = uVar6 | param_2 >> 1;
    uVar1 = uVar4 >> 1;
    uVar4 = uVar4 >> 1;
  } while (uVar1 != 0);
  *param_1 = uVar2;
  return (int)uVar3;
}

