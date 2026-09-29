
void Cy_SysTick_ServiceCallbacks(void)

{
  code *pcVar1;
  uint uVar2;
  
  if (*DAT_0000a618 << 0xf < 0) {
    for (uVar2 = 0; uVar2 < 5; uVar2 = uVar2 + 1) {
      pcVar1 = *(code **)(uVar2 * 4 + DAT_0000a61c);
      if (pcVar1 != (code *)0x0) {
        (*pcVar1)();
      }
    }
  }
  return;
}

