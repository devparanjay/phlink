# Plan 10-04 — Linux updater path (AppImage + system-pkg detect)

**Phase**: 10  ·  **Plan**: 10-04  ·  **Atomic patch slot**: 0127
**Depends on**: 10-02

## Outcome

On Linux, `UpdaterService` distinguishes three install modes and behaves
correctly in each:

1. **AppImage** — full self-update path (download new `.AppImage`, verify
   TUF target SHA + GPG detached signature, swap file, restart).
2. **`.deb` / `.rpm`** — detect via `/proc/self/exe` path under `/usr/`
   plus the presence of a system package manager; **disable** in-app
   updates with a "Updates managed by your system package manager" notice
   surfaced in the eventual settings UI (10-06).
3. **Unsigned/dev** — disable as on macOS.

## Key steps

1. New `phlink_update_helper_linux` GN target — small C++ binary that
   performs the AppImage swap (write new file, `chmod +x`, atomic rename,
   `execv` the new image).
2. `UpdaterService` Linux specialization: detect mode, gate behavior.
3. GPG verification via gnupg subprocess (or libgpgme if licensing OK; fall
   back to gpg shell-out under strict env).
4. Unit tests for mode detection (`/proc/self/exe` probing mocked).
