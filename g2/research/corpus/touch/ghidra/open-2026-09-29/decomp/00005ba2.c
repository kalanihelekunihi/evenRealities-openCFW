
void touch_select_28a2_dispatch(int param_1)

{
  byte bVar1;
  
  bVar1 = *(byte *)(param_1 + 0x7b);
  if (bVar1 < 4) {
    if (1 < bVar1) {
      touch_select_2794_update();
    }
  }
  else if (bVar1 == 6) {
    touch_state_270a_update_lanes();
  }
  return;
}

