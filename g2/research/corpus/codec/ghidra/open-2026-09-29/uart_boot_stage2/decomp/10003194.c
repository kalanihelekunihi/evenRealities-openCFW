
void gx_dcache_enable(void)

{
  undefined4 *puVar1;
  
  puVar1 = puRam100031b0;
  stub();
  stub();
  puRam100031b0[1] = 1;
  *puVar1 = 0x15;
  stub();
  stub();
  return;
}

