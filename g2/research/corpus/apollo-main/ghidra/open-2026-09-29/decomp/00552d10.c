
void text_stream_reset(int *param_1)

{
  if (param_1 != (int *)0x0) {
    text_stream_stop_animation(param_1);
    if (*param_1 != 0) {
      *(undefined1 *)*param_1 = 0;
    }
    if (param_1[1] != 0) {
      *(undefined1 *)param_1[1] = 0;
    }
    param_1[3] = 0;
    param_1[4] = 0;
  }
  return;
}

