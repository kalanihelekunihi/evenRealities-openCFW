
void gx8002_snpu_isr(void)

{
  if (*DAT_10205cf0 != 2) {
    gx8002_snpu_process_status();
  }
  return;
}

