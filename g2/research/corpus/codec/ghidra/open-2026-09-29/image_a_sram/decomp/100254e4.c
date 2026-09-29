
void gx8002_irq_restore_enabled(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puVar2 = puRam100254f8;
  puVar1 = puRam100254f4;
  *puRam100254f8 = *puRam100254f4;
  puVar2[1] = puVar1[1];
  return;
}

