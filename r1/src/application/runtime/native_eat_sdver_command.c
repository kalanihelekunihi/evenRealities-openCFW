/* Stock 0x4ee82: log the SoftDevice version diagnostic. */
extern void r1_eat_ble_version_log(void);

void r1_eat_callback_0004ee82(char *argument)
{
    (void)argument;
    r1_eat_ble_version_log();
}
