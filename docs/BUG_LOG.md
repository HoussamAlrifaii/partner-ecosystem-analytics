# Bugs and learning evidence

## 001 SQLite connection lifetime

Found during implementation review on 2026-09-10. The first draft wrapped sqlite3.connect in a connection context manager and then moved its output directory. That context controls commit/rollback, but does not close the connection. An open handle is an unnecessary resource leak and can prevent moving database files on platforms with different locking behavior.

Fix: use contextlib.closing for the connection and explicitly commit before leaving the block. The warehouse handle is closed before version publication. Validation: the final integration tests successfully create/read/reuse versioned databases and preserve the last successful pointer when reference validation fails. The final suite contains 13 passing tests on Linux. We did not reproduce a Windows file-lock exception and do not claim that we did.

Interview account: 'During review I noticed I was treating the transaction context as a resource-lifetime context. I separated commit from close so the publication step operates on a closed database. The local integration suite passed, and I documented that Windows-specific behavior remains untested.'

Reference: [Python SQLite connection contexts](https://docs.python.org/3.12/library/sqlite3.html#how-to-use-the-connection-context-manager).

## Deliberate data defects are not discovered code bugs

The generator intentionally includes five invalid latest records, older revisions and duplicate exports. They prove validation behavior; they are not described as defects found in an employer's system. No failed model, sales uplift or production incident is invented for an interview story.
