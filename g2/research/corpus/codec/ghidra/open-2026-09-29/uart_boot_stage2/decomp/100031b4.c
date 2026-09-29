
void gx_dcache_disable(void)

{
  uint *puVar1;
  
  puVar1 = puRam100031d4;
  stub();
  stub();
  *puRam100031d4 = *puRam100031d4 & 0xfffffffe;
  puVar1[1] = 1;
  stub();
  stub();
  return;
}

