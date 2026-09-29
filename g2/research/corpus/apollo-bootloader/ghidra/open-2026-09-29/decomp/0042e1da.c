
void control_terminal_loop_42e1da(void)

{
  event_bit_set_42e444(1);
  do {
    bl_runtime_notify(0xffffffff);
  } while( true );
}

