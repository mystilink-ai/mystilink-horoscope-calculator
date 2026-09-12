#include "mystilink_horoscope.h"

#include <stdio.h>
#include <stdlib.h>

int main(void) {
  const char *argv[] = {
      "natal",
      "--datetime",
      "1990-06-15 14:30",
      "--timezone",
      "Asia/Shanghai",
      "--lat",
      "31.2304",
      "--lon",
      "121.4737",
      NULL,
  };
  char *json = NULL;
  int rc = mystilink_horoscope_run(argv, &json);
  if (rc != 0) {
    fprintf(stderr, "CLI failed (%d)\n%s\n", rc, json ? json : "");
    free(json);
    return 1;
  }
  fputs(json, stdout);
  free(json);
  return 0;
}
