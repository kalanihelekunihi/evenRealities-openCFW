
/* WARNING: Removing unreachable block (ram,0x100124d2) */

void FUN_10012470(uint *param_1,undefined4 *param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = (*(ushort *)((int)param_1 + 2) & 0x3fff) >> 7;
  uVar4 = *param_1 & 0x3fffff;
  param_2[1] = (uint)(*(byte *)((int)param_1 + 3) >> 7);
  if (uVar2 != 0) {
    if (uVar2 == 0xff) {
      if (uVar4 == 0) {
        *param_2 = 4;
      }
      else {
        *param_2 = 0;
        param_2[3] = uVar4 << 7 & DAT_100124e8;
      }
    }
    else {
      param_2[2] = uVar2 - 0x7f;
      *param_2 = 3;
      param_2[3] = uVar4 << 7 | 0x40000000;
    }
    return;
  }
  if (uVar4 == 0) {
    *param_2 = 2;
    return;
  }
  *param_2 = 3;
  uVar4 = uVar4 << 7;
  iVar1 = -0x7f;
  do {
    iVar3 = iVar1;
    uVar4 = uVar4 * 2;
    iVar1 = iVar3 + -1;
  } while (uVar4 < 0x40000000);
  param_2[2] = iVar3;
  param_2[3] = uVar4;
  return;
}

