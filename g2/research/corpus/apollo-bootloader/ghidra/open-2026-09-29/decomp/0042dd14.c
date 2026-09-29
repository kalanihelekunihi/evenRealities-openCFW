
void control_orchestrator_42dd14(void)

{
  uint uVar1;
  
  control_one_wrapper_42dd9a();
  runtime_queue_context_init_42dd70();
  runtime_context_wrapper_42dd68();
  noop_callback_0042dd98();
  control_two_wrapper_42dda4();
  do {
    while ((uVar1 = bl_runtime_wait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000))) {
      control_bits_dispatch_42e1c4();
    }
    elog_output(1,DAT_0042e118,DAT_0042e114,PTR_s_thread_dfu_0042e16c,0x199,
                PTR_s_Notify_error__0042e168);
  } while( true );
}

