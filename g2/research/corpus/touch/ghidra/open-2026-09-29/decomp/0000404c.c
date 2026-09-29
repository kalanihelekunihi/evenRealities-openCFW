
void touch_startup_0d4c_initialize(undefined2 *param_1,undefined2 *param_2)

{
  if ((param_1 != (undefined2 *)0x0) && (param_2 != (undefined2 *)0x0)) {
    memset(param_1,0,0x50);
    *param_1 = *param_2;
    timeout_default_1000_if_zero(param_1);
  }
  return;
}

