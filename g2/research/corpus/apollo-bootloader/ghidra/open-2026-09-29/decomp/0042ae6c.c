
void spotmgr_trim_restore_42ae6c(void)

{
  if (*DAT_0042b6ac == '\0') {
    *DAT_0042b6b0 = *DAT_0042b6b0 & 0xffffff80 | *DAT_0042b6b4 & 0x7f;
    *DAT_0042b9c0 = *DAT_0042b9c0 & 0xffffff80 | *DAT_0042b9c4 & 0x7f;
  }
  return;
}

