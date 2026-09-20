#include "mystilink_horoscope.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <sys/wait.h>
#endif

#define MH_BUF 4096

static const char *resolve_cli(void) {
  const char *env = getenv("MYSTILINK_HOROSCOPE_CLI");
  if (env && env[0]) {
    return env;
  }
  return "horoscope";
}

static char *read_all(FILE *fp) {
  size_t cap = MH_BUF;
  size_t len = 0;
  char *buf = (char *)malloc(cap);
  if (!buf) {
    return NULL;
  }
  for (;;) {
    if (len + MH_BUF > cap) {
      cap *= 2;
      char *nbuf = (char *)realloc(buf, cap);
      if (!nbuf) {
        free(buf);
        return NULL;
      }
      buf = nbuf;
    }
    size_t n = fread(buf + len, 1, MH_BUF - 1, fp);
    len += n;
    if (n < MH_BUF - 1) {
      break;
    }
  }
  buf[len] = '\0';
  return buf;
}

int mystilink_horoscope_run(const char *const *argv, char **out_json) {
  if (!out_json) {
    return 2;
  }
  *out_json = NULL;

  const char *cli = resolve_cli();
  size_t argc = 0;
  while (argv && argv[argc]) {
    argc++;
  }

#ifdef _WIN32
  /* Build command line and run via _popen for portability in this thin binding. */
  size_t need = strlen(cli) + 3;
  for (size_t i = 0; i < argc; i++) {
    need += strlen(argv[i]) + 3;
  }
  char *cmd = (char *)malloc(need);
  if (!cmd) {
    return 3;
  }
  strcpy(cmd, "\"");
  strcat(cmd, cli);
  strcat(cmd, "\"");
  for (size_t i = 0; i < argc; i++) {
    strcat(cmd, " \"");
    strcat(cmd, argv[i]);
    strcat(cmd, "\"");
  }
  FILE *fp = _popen(cmd, "r");
  free(cmd);
  if (!fp) {
    return 4;
  }
  *out_json = read_all(fp);
  int rc = _pclose(fp);
  return rc == 0 ? 0 : 1;
#else
  int pipefd[2];
  if (pipe(pipefd) != 0) {
    return 4;
  }
  pid_t pid = fork();
  if (pid < 0) {
    close(pipefd[0]);
    close(pipefd[1]);
    return 4;
  }
  if (pid == 0) {
    close(pipefd[0]);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);
    char **child_argv = (char **)calloc(argc + 2, sizeof(char *));
    if (!child_argv) {
      _exit(127);
    }
    child_argv[0] = (char *)cli;
    for (size_t i = 0; i < argc; i++) {
      child_argv[i + 1] = (char *)argv[i];
    }
    child_argv[argc + 1] = NULL;
    execvp(cli, child_argv);
    _exit(127);
  }
  close(pipefd[1]);
  FILE *fp = fdopen(pipefd[0], "r");
  if (!fp) {
    close(pipefd[0]);
    waitpid(pid, NULL, 0);
    return 4;
  }
  *out_json = read_all(fp);
  fclose(fp);
  int status = 0;
  waitpid(pid, &status, 0);
  if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
    return 0;
  }
  return 1;
#endif
}
