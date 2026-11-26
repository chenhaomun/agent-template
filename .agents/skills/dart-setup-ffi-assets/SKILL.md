---
name: dart-setup-ffi-assets
stack: dart
description: Compile or bundle C/C++ code as Dart native code assets with `hook/build.dart` and `hook/link.dart`. Use only with explicit approval for native/FFI work.
---

# Native Code Assets

AGENTS.md requires explicit approval for native, FFI, and binary-download work. Confirm scope, target platforms, and host toolchain availability before starting; reuse existing hooks if present.

## Setup

- Dependencies (approval required): `hooks`, `code_assets`, `native_toolchain_c`, plus `record_use` and dev `ffigen` when tree-shaking.
- Keep one library spec (for example `lib/src/c_library.dart` with `CLibrary` or `CBuilder`) shared by both hooks.
- Hooks live only in `hook/`. Resolve paths with `Uri`/`Platform.script.resolve`; never hard-code absolute paths or call compilers through shell commands.
- Put the package's own copyright header on hand-written hooks and helpers; generated bindings carry the native library's license.
- Declare exported symbols for Windows DLLs (for example a `__declspec(dllexport)` define when `targetOS` is Windows).

## Build options

- **Local compile (preferred):** `hook/build.dart` builds when `input.config.buildCodeAssets`; `hook/link.dart` can use `LinkerOptions.treeshake` with an ffigen-generated `record_use` mapping (`lib/src/third_party/*.g.dart`). Needs a host C toolchain; report when it is missing instead of installing one.
- **Precompiled download:** only with approval. Pin the version, verify each file against a checked-in SHA-256 hash before registering it as a `CodeAsset`, fail closed on mismatch, and support an offline `local_build` user define that compiles from source.

## Verify

- Run the affected tests so the hook cycle executes, and confirm the library is produced for the host.
- When tree-shaking, build a release bundle and check exported symbols (`nm -gU`, `nm -D`, or `dumpbin /EXPORTS`).
- Check the offline path with `local_build: true` when downloads exist.
- Report every platform and toolchain not exercised.
