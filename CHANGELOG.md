# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-09

### Added

- Automatic creation of the `~/Desktop/fix_keynote` directory on app startup with an informative popup guiding the user.
- User-friendly native alert if the `fix_keynote` folder is empty, instructing them to add corrupted files.
- Project information in the `pyproject.toml` file.

## [0.2.0] - 2026-03-06

### Added

- Automated publishing to PyPI (Python Package Index) via GitHub Actions using Trusted Publishing.
- Added documentation in the README regarding the macOS Gatekeeper workaround for unsigned applications.

## [0.1.0] - 2026-03-06

### Added

- Initial release of the FixKeynote application.
- Extraction of text, presenter notes, and images from corrupted Keynote (`.key`) files.
- Automated presentation reconstruction via AppleScript, preserving the presumed slide order.
- Standalone macOS application (Generated via `PyInstaller`).
- Native macOS dialog boxes for success and error messages.
- Automatic revelation of the repaired file or folder in Finder upon completion.
- Fallback mechanism to a "Blank" or "Vierge" slide layout if the default theme changes based on the user's macOS locale.
