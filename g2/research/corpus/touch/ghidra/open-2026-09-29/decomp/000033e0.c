
void FUN_000033e0(void)

{
  if (((DAT_00003400 - DAT_000033fc >> 2) - (DAT_00003400 - DAT_000033fc >> 0x1f) >> 1 != 0) &&
     (DAT_00003404 != (code *)0x0)) {
    (*DAT_00003404)();
  }
  return;
}

