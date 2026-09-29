
void tt_face_done_loca(int param_1)

{
  FT_Stream_ReleaseFrame(*(undefined4 *)(param_1 + 0x68),param_1 + 0x2d8);
  *(undefined4 *)(param_1 + 0x2d4) = 0;
  return;
}

