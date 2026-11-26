---
name: dart-use-primary-constructors
stack: dart
description: Write or migrate to Dart primary constructors and concise constructor syntax. Use only when the project's SDK constraint supports them (Dart 3.13+, or 3.12 with the experiment enabled) and they are requested or already used.
---

# Primary Constructors

Check `environment: sdk` in `pubspec.yaml` first. Do not enable the experiment flag or migrate existing classes unless asked; follow the project's current constructor style otherwise.

## Syntax

- Header parameters: `final`/`var` declare fields, `this.`/`super.` initialize existing ones, plain parameters exist only during initialization. Example: `class Point(final int x, final int y);`
- `const` goes before the type name: `class const Point(final int x, final int y);`
- Initializer list, asserts, or body go in `this : ...;` or `this { ... }` inside the class body.
- Non-late field initializers can read header parameters; `late` initializers cannot.
- Other generative constructors must redirect to the primary one (`new zero() : this(0, 0);`).
- In-body constructors may use `new`/`factory` in place of the class name.
- Empty bodies may be `;`. Extension types always use a primary constructor; the representation parameter cannot be `var`.

## Errors

- Assigning a parameter during initialization, or initializing a field twice, is a compile error.
- A non-redirecting in-body generative constructor alongside a primary constructor is invalid.

## Migrate (when requested)

Move fields into the header, move initializer lists and asserts into `this :`, turn derived fields into body initializers, make other constructors redirect, then run analysis and tests. Keep the migration to the classes in scope.
