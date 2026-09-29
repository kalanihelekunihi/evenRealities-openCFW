
void FUN_0800ae0c(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *puVar5;
  
  puVar1 = DAT_0800ae54;
  iVar4 = 0xc00;
  puVar2 = DAT_0800ae50;
  if (((uint)DAT_0800ae50 & 7) != 0) {
    puVar2 = (undefined4 *)((int)DAT_0800ae50 + 7U & 0xfffffff8);
    iVar4 = 0xc00 - ((int)puVar2 - (int)DAT_0800ae50);
  }
  *DAT_0800ae54 = puVar2;
  puVar1[1] = 0;
  puVar1 = DAT_0800ae58;
  puVar5 = (undefined4 *)((int)puVar2 + iVar4 + -8 & 0xfffffff8);
  *DAT_0800ae58 = puVar5;
  puVar5[1] = 0;
  *puVar5 = 0;
  puVar2[1] = (int)puVar5 - (int)puVar2;
  *puVar2 = puVar5;
  uVar3 = puVar2[1];
  puVar1[2] = uVar3;
  puVar1[1] = uVar3;
  puVar1[5] = 0x80000000;
  return;
}

