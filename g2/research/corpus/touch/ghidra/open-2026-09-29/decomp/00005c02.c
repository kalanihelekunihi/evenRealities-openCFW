
void touch_state_2902_cap_enabled_object(int param_1,int param_2)

{
  if (*(char *)(*(int *)(param_2 + 0xc) + param_1 * 0x90 + 0x7b) != '\a') {
    touch_state_28c0_cap_object();
  }
  return;
}

