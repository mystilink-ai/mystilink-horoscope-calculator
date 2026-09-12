#ifndef MYSTILINK_HOROSCOPE_H
#define MYSTILINK_HOROSCOPE_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Spawn the mystilink-horoscope CLI (or MYSTILINK_HOROSCOPE_CLI) and capture JSON.
 * argv is a NULL-terminated list of CLI arguments AFTER the program name
 * (e.g. "natal", "--datetime", "...", NULL).
 * On success returns 0 and writes malloc'd UTF-8 JSON to *out_json (caller frees).
 * On failure returns non-zero; *out_json may be NULL or hold stderr text.
 */
int mystilink_horoscope_run(const char *const *argv, char **out_json);

#ifdef __cplusplus
}
#endif

#endif /* MYSTILINK_HOROSCOPE_H */
