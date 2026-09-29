
void gx8002_clear_bss(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puVar1 = puRam10023544;
  for (puVar2 = puRam10023548; puVar2 < puVar1; puVar2 = puVar2 + 1) {
    *puVar2 = 0;
  }
  return;
}

