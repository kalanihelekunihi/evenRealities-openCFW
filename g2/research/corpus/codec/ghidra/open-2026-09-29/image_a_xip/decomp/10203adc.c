
undefined4 gx8002_dma_irq_handler(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  
  iVar2 = iRam10203b34;
  piVar1 = piRam10203b30;
  uVar4 = 0;
  iVar5 = *(int *)(*piRam10203b30 + 0x2e8);
  iVar6 = iRam10203b34 + 8;
  do {
    if ((iVar5 >> (uVar4 & 0x3f) & 1U) != 0) {
      gx8002_dma_clear(uVar4);
      *(int *)(*piVar1 + 0x310) = 0x100 << (uVar4 & 0x3f);
      gx8002_dma_deallocate(uVar4);
      uVar3 = *(uint *)(iVar2 + uVar4 * 4);
      if (uVar3 != 0) {
        (*(code *)(uVar3 & 0xfffffffe))(*(undefined4 *)(iVar6 + uVar4 * 4));
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 != 2);
  return 0;
}

