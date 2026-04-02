/*
 * Thin universal-binary wrapper for the pyrunner .app bundle.
 *
 * macOS LaunchServices cannot determine the architecture of a shell script
 * used as CFBundleExecutable, which triggers a Rosetta prompt on Apple
 * Silicon.  This native stub resolves that by exec-ing the real launcher
 * script (launch.sh) located alongside this binary.
 */

#include <mach-o/dyld.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    char path[4096];
    uint32_t size = sizeof(path);

    if (_NSGetExecutablePath(path, &size) != 0) {
        return 1;
    }

    /* Replace trailing "launch" with "launch.sh" */
    char *last_slash = strrchr(path, '/');
    if (!last_slash) {
        return 1;
    }
    strcpy(last_slash + 1, "launch.sh");

    execl("/bin/bash", "bash", path, (char *)NULL);
    /* execl only returns on error */
    perror("execl");
    return 1;
}
