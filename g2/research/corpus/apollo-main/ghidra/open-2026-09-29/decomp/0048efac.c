
void threadBleMsgRxDispatchFlags(int param_1)

{
  if (param_1 << 9 < 0) {
    _thread_pb_msg_handler();
  }
  if (param_1 << 8 < 0) {
    _thread_exit();
  }
  return;
}

