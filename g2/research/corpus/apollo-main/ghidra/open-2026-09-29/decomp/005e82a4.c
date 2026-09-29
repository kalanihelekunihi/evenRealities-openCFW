
undefined * semantic_terminal_session_status_name(byte param_1)

{
  undefined *puVar1;
  
  puVar1 = PTR_s_SESSION_STATUS_NONE_005e8c24;
  if ((((param_1 != 0) && (puVar1 = PTR_s_SESSION_STATUS_AWAIT_USER_005e8c2c, param_1 != 2)) &&
      (puVar1 = PTR_s_SESSION_STATUS_THINKING_005e8c28, 1 < param_1)) &&
     (((puVar1 = PTR_s_SESSION_STATUS_RESET_005e8c34, param_1 != 4 &&
       (puVar1 = PTR_s_SESSION_STATUS_DONE_005e8c30, 3 < param_1)) &&
      (puVar1 = PTR_s_SESSION_STATUS_SYNC_END_005e8c38, param_1 != 5)))) {
    puVar1 = PTR_s_SESSION_STATUS_UNKNOWN_005e8e3c;
  }
  return puVar1;
}

