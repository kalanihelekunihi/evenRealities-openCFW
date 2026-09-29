
void touch_platform_11a0_sequence(void)

{
  touch_clock_12d0_transition();
  touch_startup_11d0_configure_dividers();
  touch_startup_1228_assign_divider();
  touch_platform_1238_routes();
  return;
}

