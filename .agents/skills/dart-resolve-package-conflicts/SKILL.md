---
name: dart-resolve-package-conflicts
stack: dart
description: Diagnose and fix `pub get` version conflicts, retracted versions, and outdated dependencies with minimal upgrades. Use when dependency resolution fails or an upgrade is requested.
---

# Resolve Package Conflicts

Use the project's SDK wrapper (for example `fvm flutter pub ...`). Read the full solver output first; it names the conflicting constraints.

## Diagnose

- Run `pub outdated` and `pub deps` to see current, upgradable, resolvable, and latest versions and which package pulls in the conflict.
- Identify the smallest change: one direct constraint, one transitive upgrade, or a retracted version.

## Fix

- Upgrade only the affected packages (`pub upgrade <package>`); never delete `pubspec.lock` or upgrade everything to make a conflict disappear.
- Change `pubspec.yaml` constraints only as far as needed, using caret ranges. A major-version bump, new package, or `dependency_overrides` needs approval; record why any override exists.
- Do not hand-edit `pubspec.lock`; let pub regenerate it. Keep SDK constraints unchanged unless the task requires it.

## Verify

Run `pub get`, analysis, and affected tests; fix breaking API changes in the same change. Report every changed constraint and resolved version.
