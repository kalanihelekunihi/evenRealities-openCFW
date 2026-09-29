
void prvHeapInit(void)

{
  uint *puVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = DAT_00456344;
  iVar3 = 0x2f000;
  puVar2 = DAT_00456354;
  if (((uint)DAT_00456354 & 7) != 0) {
    puVar2 = (uint *)((int)DAT_00456354 + 7U & 0xfffffff8);
    iVar3 = (int)DAT_00456354 + (0x2f000 - (int)puVar2);
  }
  *DAT_00456344 = (uint)puVar2;
  puVar1[1] = 0;
  puVar1 = DAT_00456338;
  uVar4 = (int)puVar2 + (iVar3 - *DAT_0045633c) & 0xfffffff8;
  *DAT_00456338 = uVar4;
  *(undefined4 *)(*puVar1 + 4) = 0;
  *(undefined4 *)*puVar1 = 0;
  puVar2[1] = uVar4 - (int)puVar2;
  *puVar2 = *puVar1;
  *DAT_00456348 = puVar2[1];
  *DAT_00456340 = puVar2[1];
  return;
}

