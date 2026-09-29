
undefined8 FUN_0044b0d6(uint param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  byte bVar5;
  byte bVar6;
  
  bVar6 = 0;
  uVar4 = FUN_00473940();
  iVar3 = DAT_0044b574;
  *(undefined1 *)(DAT_0044b574 + (param_1 & 0xff)) = param_2;
  puVar2 = DAT_0044b570;
  for (bVar5 = 0; bVar5 < 6; bVar5 = bVar5 + 1) {
    bVar6 = bVar6 | *(byte *)(iVar3 + (uint)bVar5);
  }
  *DAT_0044b570 = *DAT_0044b570 & 0xfffffffd | (bVar6 & 1) << 1;
  *puVar2 = *puVar2 & 0xfffffffb | (bVar6 >> 1 & 1) << 2;
  *puVar2 = *puVar2 & 0xfffffff7 | (bVar6 >> 2 & 1) << 3;
  *puVar2 = *puVar2 & 0xffffffef | (bVar6 >> 3 & 1) << 4;
  *puVar2 = *puVar2 & 0xffffffdf | (bVar6 >> 4 & 1) << 5;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar4 & 1) == 1);
  }
  return CONCAT44(param_4,uVar4);
}

