
void gx_icache_enable(void)

{
  uRamb0000000 = 1;
  do {
  } while ((uRamb0000004 & 3) != 2);
  return;
}

