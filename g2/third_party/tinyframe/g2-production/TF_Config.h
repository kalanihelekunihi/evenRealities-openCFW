#ifndef OPEN_CFW_TINYFRAME_G2_PRODUCTION_CONFIG_H
#define OPEN_CFW_TINYFRAME_G2_PRODUCTION_CONFIG_H

/*
 * Keep the authenticated recovered G2 protocol/ABI configuration intact, but
 * make diagnostics an explicit production policy.  TinyFrame logging has no
 * wire or state-machine effect, and a no-op avoids retaining or guessing the
 * stock EasyLogger vararg ABI during atomic source routing.
 */
#include "../g2-config/TF_Config.h"

#undef TF_Error
#define TF_Error(format, ...) ((void)(format))

#endif
