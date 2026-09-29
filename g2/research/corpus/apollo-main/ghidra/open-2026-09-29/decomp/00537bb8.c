
bool smpStateIdle(int param_1)

{
  return *(char *)(param_1 + 0x3e) == '\0';
}

