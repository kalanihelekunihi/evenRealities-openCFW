
bool HciLeAdvExtSupported(void)

{
  return *(char *)(DAT_00530d68 + 0x91) != '\0';
}

