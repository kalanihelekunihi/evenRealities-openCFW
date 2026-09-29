
void aud_thread_flag_dispatch(int param_1)

{
  if (param_1 << 9 < 0) {
    aud_message_loop();
  }
  if (param_1 << 8 < 0) {
    AUD_ThreadExit();
  }
  return;
}

