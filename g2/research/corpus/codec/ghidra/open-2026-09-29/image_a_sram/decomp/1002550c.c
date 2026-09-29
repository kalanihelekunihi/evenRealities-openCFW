
void gx8002_irq_save_disable(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  
  puVar2 = puRam10025530;
  puVar1 = puRam1002552c;
  *puRam10025530 = *puRam1002552c;
  puVar2[1] = puVar1[1];
  iVar3 = 0;
  do {
    iVar4 = iVar3 + 1;
    csi_vic_disable_irq(iVar3);
    iVar3 = iVar4;
  } while (iVar4 != 0x20);
  return;
}

