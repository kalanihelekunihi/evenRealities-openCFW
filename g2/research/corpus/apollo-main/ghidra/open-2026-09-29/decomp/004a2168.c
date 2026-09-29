
bool auth_mode_set(byte param_1)

{
  if (param_1 < 0x5a) {
    *DAT_004a2c74 = param_1;
  }
  return *DAT_004a2c74 != 0;
}

