#ifndef OPENR1_R1_PERSISTENCE_H
#define OPENR1_R1_PERSISTENCE_H

#include "openr1/r1_health.h"
#include "openr1/r1_sleep_db.h"

r1_error r1_sleep_persist(r1_sleep_db *database, const r1_sleep_session *session);
r1_error r1_sleep_persist_tracked(r1_sleep_db *database, r1_sleep_session *session);
r1_error r1_sleep_restore(r1_sleep_db *database, r1_sleep_history *history);
r1_error r1_sleep_commit_synchronized(void *context,
                                      const r1_sleep_session *session);

#endif
