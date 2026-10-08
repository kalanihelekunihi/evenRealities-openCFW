/* Include from the main SECTIONS body. Keep this at the locked data VA while
 * retaining source relocations for each callback pointer. */
. = 0x433440;
.boot_initializer_callbacks :
{
    KEEP(*(.boot_initializer_callbacks))
}
. = 0x433D58;
.boot_context_config :
{
    KEEP(*(.boot_context_config))
}
