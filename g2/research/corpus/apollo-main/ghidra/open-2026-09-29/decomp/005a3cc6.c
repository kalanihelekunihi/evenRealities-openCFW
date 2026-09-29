
uint FUN_005a3cc6(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  bool bVar8;
  undefined4 local_28;
  
  puVar4 = (uint *)(DAT_005a4104 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_005a4104 + 100);
  local_28 = CONCAT13((char)(*puVar3 >> 0x15),
                      CONCAT12((char)(*puVar3 >> 0xe),
                               CONCAT11((char)(*puVar3 >> 7),*(undefined1 *)puVar3))) & 0x7f7f7f7f;
  uVar5 = *(byte *)(DAT_005a4104 + param_2 * 4 + 4) & 0x7f;
  uVar2 = *puVar4;
  uVar6 = *(byte *)puVar4 & 0x7f;
  if (*DAT_005a4108 << 0x1f < 0) {
    uVar7 = 0;
    while ((uVar7 < 0x3c && (-1 < *DAT_005a4234 << 1))) {
      FUN_004807a0(1);
      uVar7 = uVar7 + 1;
    }
    FUN_005a40ca();
  }
  *DAT_005a4238 = param_3;
  *DAT_005a4324 = param_1;
  *DAT_005a4328 = (*puVar4 & 0x1ffff) >> 7;
  *DAT_005a432c = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_005a4330 = (uVar2 & 0xfffffff) >> 0x15;
  *DAT_005a40fc = uVar6;
  *DAT_005a45cc = 1;
  FUN_005a423c(param_3,param_1);
  if ((int)(uVar6 - uVar5) < 1) {
    iVar1 = 0;
  }
  else {
    iVar1 = (uVar6 - uVar5) * 2;
  }
  if (iVar1 + uVar5 < 0x80) {
    *DAT_005a3e20 = *DAT_005a3e20 & 0xffffff80 | iVar1 + uVar5 & 0x7f;
  }
  else {
    *DAT_005a3e20 = *DAT_005a3e20 | 0x7f;
  }
  FUN_004807a0(0x32);
  *DAT_005a3e20 = uVar6 | *DAT_005a3e20 & 0xffffff80;
  bVar8 = *DAT_005a48e0 << 0xe < 0;
  if (bVar8) {
    FUN_00474efa();
  }
  puVar3 = DAT_005a48e4;
  *DAT_005a48e4 = *DAT_005a48e4 | 0x10000;
  *puVar3 = *puVar3 | 0x2000000;
  FUN_004807a0(0x14);
  if (bVar8) {
    FUN_00474eb4();
  }
  return local_28;
}

