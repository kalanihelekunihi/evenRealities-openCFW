
void gx8002_event_notify(undefined4 param_1)

{
  gx8002_notification_stamp();
  gx8002_app_reply(1,0xc,param_1);
  return;
}

