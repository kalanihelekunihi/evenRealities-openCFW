
bool wsfOsReadyToSleep(void)

{
  return *(char *)(DAT_0052bac4 + 0x3c) == '\0';
}

