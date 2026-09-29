
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx8002_backup_clear_bss(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puVar1 = _gx8002_backup_bss_bounds;
  for (puVar2 = puRam10003148; puVar2 < puVar1; puVar2 = puVar2 + 1) {
    *puVar2 = 0;
  }
  return;
}

