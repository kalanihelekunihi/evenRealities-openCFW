
void case_add_byte0_to_word8(void)

{
  *(uint *)(DAT_08004ee8 + 8) = *(int *)(DAT_08004ee8 + 8) + (uint)*DAT_08004ee8;
  return;
}

