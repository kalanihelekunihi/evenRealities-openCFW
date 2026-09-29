
void semantic_terminal_runtime_event_callback(int param_1,char *param_2)

{
  char cVar1;
  
  if ((param_1 == 0) && (param_2 != (char *)0x0)) {
    cVar1 = *param_2;
    if (cVar1 == '\0') {
      td_notify_state_clear();
      td_session_struct_clear();
    }
    terminal_request_runtime_event_if_allowed(cVar1 != '\0');
  }
  return;
}

