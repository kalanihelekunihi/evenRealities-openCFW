
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void text_stream_animation_presets_deinit(void)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  
  pcVar1 = DAT_00553d44;
  if (*DAT_00553d44 != '\0') {
    for (iVar3 = 0; iVar2 = DAT_00553d60, iVar3 < 4; iVar3 = iVar3 + 1) {
      if (*(int *)(DAT_00553d60 + iVar3 * 4) != 0) {
        FUN_00463e1c(*(undefined4 *)(DAT_00553d60 + iVar3 * 4),0);
        *(undefined4 *)(iVar2 + iVar3 * 4) = 0;
      }
    }
    FUN_0043c0e4(DAT_00553d5c,0x34,0);
    FUN_0043c0e4(DAT_00553fec,0x40,0);
    *_DAT_00553d48 = 0;
    *pcVar1 = '\0';
    *DAT_00553fe8 = 0;
  }
  return;
}

