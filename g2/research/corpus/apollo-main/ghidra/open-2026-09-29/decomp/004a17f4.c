
void central_cancel_connect_retry_work_004a17f4(void)

{
  char *pcVar1;
  
  pcVar1 = DAT_004a2364;
  if (*DAT_004a2364 == '\x01') {
    central_emit_ring_link_event_004a153c(6);
  }
  *pcVar1 = '\0';
  fw_event_loop_remove_delayed(0x4a1b61);
  return;
}

