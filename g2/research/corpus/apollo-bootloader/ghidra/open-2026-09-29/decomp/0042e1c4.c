
void control_bits_dispatch_42e1c4(int param_1)

{
  if (param_1 << 9 < 0) {
    dfu_service_task_42de58();
  }
  if (param_1 << 8 < 0) {
    control_terminal_loop_42e1da();
  }
  return;
}

