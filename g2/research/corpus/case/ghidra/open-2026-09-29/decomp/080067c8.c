
void log_hex_buffer(int param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = DAT_080067fc;
  if (*(char *)(DAT_080067fc + 7) == '\0') {
    for (uVar2 = 0; uVar2 < param_2; uVar2 = uVar2 + 1 & 0xffff) {
      if (*(char *)(iVar1 + 7) == '\0') {
        g2_log_printf(s__02x_08006800,*(undefined1 *)(param_1 + uVar2));
      }
    }
    if (*(char *)(iVar1 + 7) == '\0') {
      g2_log_printf(&DAT_08006808);
    }
  }
  return;
}

