
void input_flags_dispatch(int param_1)

{
  if (param_1 << 9 < 0) {
    input_queue_drain();
  }
  if (param_1 << 8 < 0) {
    INP_ThreadExit();
  }
  return;
}

