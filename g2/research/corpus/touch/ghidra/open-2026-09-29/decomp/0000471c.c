
void touch_runtime_141c_handoff(void)

{
  *(undefined4 *)(DAT_0000472c + 0x38) = DAT_00004730;
  disableIRQinterrupts();
  touch_leaf_1418_passthrough();
  return;
}

