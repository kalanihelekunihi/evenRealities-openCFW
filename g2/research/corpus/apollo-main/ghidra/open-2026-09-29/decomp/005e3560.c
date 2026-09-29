
undefined8 smpiScActPkCalcCa(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  byte bVar2;
  uint uVar3;
  undefined4 uVar4;
  
  puVar1 = PTR_DAT_005e38b0;
  if (*(char *)(*(int *)(param_1 + 0x48) + 3) == '\0') {
    FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x20,PTR_DAT_005e38b0,param_3,param_4,
                 param_3,param_4);
    FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x30,puVar1);
    if (*(byte *)(param_2 + 0x14) < 4) {
      WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x2d,param_2 + 4,
                     *(undefined1 *)(param_2 + 0x14));
      WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x3d,param_2 + 4,
                     *(undefined1 *)(param_2 + 0x14));
    }
  }
  FUN_0053634e(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),0x10);
  smpLogByteArray(PTR_s_Rand_Na_005e38ac,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),0x10);
  bVar2 = smpGetPkBit(param_1);
  uVar4 = *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14);
  uVar3 = (uint)bVar2;
  SmpScCalcF4(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),
              *(undefined4 *)(*(int *)(param_1 + 0x48) + 8));
  return CONCAT44(uVar4,uVar3);
}

