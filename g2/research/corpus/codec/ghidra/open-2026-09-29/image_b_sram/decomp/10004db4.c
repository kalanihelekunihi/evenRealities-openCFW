
void gx_dcache_disable(void)

{
  uint *puVar1;
  
  puVar1 = puRam10004dd4;
  stub();
  stub();
  *puRam10004dd4 = *puRam10004dd4 & 0xfffffffe;
  puVar1[1] = 1;
  stub();
  stub();
  return;
}

