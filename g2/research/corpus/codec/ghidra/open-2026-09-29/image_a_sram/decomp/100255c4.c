
void gx_dcache_enable(void)

{
  undefined4 *puVar1;
  
  puVar1 = puRam100255e0;
  stub();
  stub();
  puRam100255e0[1] = 1;
  *puVar1 = 0x15;
  stub();
  stub();
  return;
}

