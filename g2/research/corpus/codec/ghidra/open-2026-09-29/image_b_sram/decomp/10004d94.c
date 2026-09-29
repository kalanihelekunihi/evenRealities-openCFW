
void gx_dcache_enable(void)

{
  undefined4 *puVar1;
  
  puVar1 = puRam10004db0;
  stub();
  stub();
  puRam10004db0[1] = 1;
  *puVar1 = 0x15;
  stub();
  stub();
  return;
}

