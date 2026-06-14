# Claude Code Android Hooks

A collection of Python-based Git hooks for Android development with Claude Code integration, designed to enforce best practices and code quality standards in Jetpack Compose projects.

## Overview

This repository contains automated hooks that integrate with Git workflows to validate Android code changes, particularly focusing on Jetpack Compose development. These hooks help ensure consistent preview implementations and catch common development issues before they reach version control.

## Features

### Compose Preview Checker

The primary hook included in this repository is `compose_preview_check.py`, which:

- **Validates Jetpack Compose Functions**: Automatically detects `@Composable` functions in Kotlin files
- **Enforces Preview Coverage**: Ensures that all zero-parameter composables have corresponding `@Preview` implementations
- **Smart Parameter Detection**: Distinguishes between parameterized and zero-argument composables
- **Flexible Search Scope**: Looks for previews in the same file and sibling `*Preview*.kt` files
- **AI-Friendly Warnings**: Provides helpful warnings for parameterized composables that need manual sample data

### Smart Differentiation

The hook categorizes missing previews into two levels:

1. **Blocking Issues** (`must_fix`): Zero-argument composables without previews
   - Prevents commit to ensure preview coverage
   - Easy for AI assistants to generate previews automatically

2. **Warnings** (`warnings`): Parameterized composables without previews
   - Alerts developer to missing previews
   - Requires manual sample data setup
   - Allows commit to proceed

## Project Structure

```
claude-code-android-hooks/
├── README.md                           # This file
└── hooks/
    └── compose/
        └── compose_preview_check.py   # Compose preview validation hook
```

## Installation

1. Clone this repository or copy the hooks directory to your Android project:

```bash
cp -r hooks /path/to/your/android/project/.git/hooks/
```

2. Make the hook executable:

```bash
chmod +x /path/to/your/android/project/.git/hooks/compose/compose_preview_check.py
```

3. Configure Git to use the hook (or set it up as a pre-commit hook in your CI/CD pipeline)

## Usage

### File Input via stdin

The hook accepts JSON input with file path information:

```json
{
  "tool_input": {
    "file_path": "path/to/YourComposable.kt"
  }
}
```

### Automatic Git Detection Fallback

If no file path is provided via stdin, the hook automatically:
- Detects unstaged changes: `git diff --name-only`
- Detects staged changes: `git diff --cached --name-only`
- Filters for `.kt` files only

### Example Output

**Success (no issues)**:
```
HOOK RUNNING
```

**With warnings (parameterized composables)**:
```
HOOK RUNNING
Warning — @Preview missing (parameterized composable; add sample data manually):
  - MyComponent (app/src/main/kotlin/ui/MyComponent.kt)
  - AnotherComponent (app/src/main/kotlin/ui/AnotherComponent.kt)
```

**With blocking issues (zero-arg composables)**:
```
HOOK RUNNING
Missing @Preview for zero-arg composable(s) — please add:
  - SimpleButton (app/src/main/kotlin/ui/SimpleButton.kt)
```

## How It Works

### 1. Composable Detection

The hook uses regex pattern matching to find `@Composable` functions:

```regex
@Composable\s*(?:\n\s*)*(?:(?:private|internal|public|protected)\s+)?fun\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(
```

This pattern captures:
- `@Composable` annotation
- Optional visibility modifiers (private, internal, public, protected)
- Function name
- Opening parenthesis

### 2. Parameter Analysis

For each composable found, the hook:
- Walks through the parameter list to find the closing `)`
- Determines if the function has parameters
- Excludes functions already named `*Preview`

### 3. Preview Search

The hook searches for `@Preview` annotations linked to the composable:
- Pattern: `@Preview[\s\S]*?\b{name}Preview\b|fun\s+{name}Preview`
- Search scope: Current file + sibling `*Preview*.kt` files

### 4. Classification & Exit Code

- **Exit 0**: No issues found or only warnings
- **Exit 2**: Blocking issues found (prevents commit)

## Requirements

- **Python 3.6+**: Uses standard library only
- **Git**: For change detection
- **Kotlin/Android Project**: With Jetpack Compose setup

## Dependencies

The script uses only Python standard library:
- `json` - Parsing hook input
- `subprocess` - Git integration
- `re` - Regex pattern matching
- `sys` - Exit codes and stdin
- `pathlib.Path` - File handling

## Integration with Claude Code

This hook is designed to work seamlessly with Claude Code AI assistants:

- **Blocking issues** are easy to resolve automatically (zero-arg composables)
- **Warnings** guide developers on what needs manual attention
- **Clear error messages** help AI understand and fix issues

## Use Cases

- ✅ Ensure all zero-parameter composables have preview implementations
- ✅ Catch missing previews before committing
- ✅ Maintain consistent preview patterns across your codebase
- ✅ Guide AI-assisted code generation for Compose functions
- ✅ Reduce manual review burden for preview coverage

## Contributing

Contributions are welcome! Feel free to:
- Report issues
- Suggest improvements
- Add additional hooks for other Android development patterns

## License

This project is provided as-is for integration with Android development workflows and Claude Code tools.

## Support

For issues, questions, or suggestions, please open an issue on this repository.

---

**Happy Composing! 🎨**
