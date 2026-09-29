
void CFF_Done_FD_Select(undefined1 *param_1,undefined4 param_2)

{
  if (*(int *)(param_1 + 8) != 0) {
    FT_Stream_ReleaseFrame(param_2,param_1 + 8);
  }
  *(undefined4 *)(param_1 + 0xc) = 0;
  *param_1 = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}

