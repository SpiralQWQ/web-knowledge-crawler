# Security Policy

## Supported Versions

We actively maintain the latest stable release. Older versions are supported on a best-effort basis.

| Version | Supported |
|---------|-----------|
| 2.x     | ✅ Yes |
| < 2.0   | ❌ No |

## Reporting a Vulnerability

Please **do not** open a public GitHub Issue for security vulnerabilities. Instead, report them privately so we can fix the issue before it is disclosed.

### How to report

1. **Open a private report** on GitHub Security Advisories:
   https://github.com/SpiralQWQ/web-knowledge-crawler/security/advisories/new
2. If you cannot use the advisory form, email the maintainers via the issue tracker's **private contact** — or open a regular issue only for *non-sensitive* problems.

### What to include

- Project name and version
- A short description of the vulnerability
- Steps to reproduce (including OS / Python version)
- Impact assessment (what an attacker could achieve)
- Any suggested fix (optional)

### What happens next

- We will acknowledge your report within **48 hours**
- We will keep you informed of the fix progress
- Once a fix is released, we will credit you for the report (if you wish)

## Security Notes for This Project

- **This tool crawls public content.** It ships **no** crawled data and downloads raw files **on demand** to the user's local disk. Never crawl content you are not authorized to access.
- **Credentials live in your local `.env`** (e.g. `GH_TOKEN`). The `.env` file is git-ignored and must **never** be committed. If you accidentally commit it, rotate the token immediately.
- **No network calls besides the sites you configure.** The tool makes requests only to the configured search/download endpoints, plus your local renderer/CDP bridges.
- **Rate limiting & robots.txt** are the user's responsibility; the tool provides built-in low-concurrency and inter-site delays to avoid hammering sites.

## Dependency Updates

We track upstream dependencies (yt-dlp, Crawl4AI, Playwright, etc.) and recommend users update regularly, as most security fixes come from these ecosystems.
