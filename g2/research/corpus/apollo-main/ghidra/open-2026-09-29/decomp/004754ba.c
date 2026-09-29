
void threadBleMsgTxDispatchFlags(int param_1)

{
  if (param_1 << 9 < 0) {
    threadBleMsgTxQueueDrain();
  }
  if (param_1 << 8 < 0) {
    threadBleMsgTxExit();
  }
  return;
}

