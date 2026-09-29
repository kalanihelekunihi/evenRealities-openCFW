
bool gx8002_power_is_locked(void)

{
  return *piRam10207804 != 0;
}

