
uint FUN_005a3fe8(int param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  undefined4 local_20;
  
  puVar4 = (uint *)(DAT_005a4104 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_005a4104 + 100);
  local_20 = CONCAT13((char)(*puVar3 >> 0x15),
                      CONCAT12((char)(*puVar3 >> 0xe),
                               CONCAT11((char)(*puVar3 >> 7),*(undefined1 *)puVar3))) & 0x7f7f7f7f;
  uVar2 = *puVar4;
  bVar1 = *(byte *)puVar4;
  if (*DAT_005a4108 << 0x1f < 0) {
    uVar5 = 0;
    while ((uVar5 < 0x3c && (-1 < *DAT_005a4234 << 1))) {
      FUN_004807a0(1);
      uVar5 = uVar5 + 1;
    }
    FUN_005a40ca();
  }
  *DAT_005a4238 = param_3;
  *DAT_005a4324 = param_1;
  *DAT_005a4328 = (*puVar4 & 0x1ffff) >> 7;
  *DAT_005a432c = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_005a4330 = (uVar2 & 0xfffffff) >> 0x15;
  *DAT_005a40fc = bVar1 & 0x7f;
  FUN_005a423c(param_3,param_1);
  return local_20;
}

