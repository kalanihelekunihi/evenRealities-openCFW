
void gx_dcache_disable(void)

{
  uint *puVar1;
  
  puVar1 = puRam10025604;
  stub();
  stub();
  *puRam10025604 = *puRam10025604 & 0xfffffffe;
  puVar1[1] = 1;
  stub();
  stub();
  return;
}

