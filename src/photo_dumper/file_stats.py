# Copyright (c) Filip Liwiński
# Licensed under the MIT License. See the LICENSE file in the project root for license information.

class FileStats:
    """
    Collects statistics of file operations.
    """

    def __init__(self):
        self._copied = 0
        self._skipped = 0
        self._conflicts = 0
        self._duplicates = 0
        self._unsupported = 0

    @property
    def total(self):
        """Returns the total number of files."""
        return self._copied + self._skipped

    @property
    def copied(self):
        """Returns the number of copied files."""
        return self._copied

    @property
    def skipped(self):
        """Returns the number of skipped files."""
        return self._skipped

    @property
    def conflicts(self):
        """Returns the number of files with name conflicts."""
        return self._conflicts

    @property
    def duplicates(self):
        """Returns the number of duplicated files."""
        return self.duplicates

    @property
    def unsupported(self):
        """Returns the number of unsupported files."""
        return self.unsupported

    def report_skipped(self):
        """Increments the number of skipped files."""
        self._skipped += 1

    def report_conflict(self):
        """Increments the number of files with name conflicts."""
        self._conflicts += 1
        self.report_skipped()

    def report_duplicate(self):
        """Increments the number of duplicated files."""
        self._duplicates += 1
        self.report_skipped()

    def report_unsupported(self):
        """Increments the number of unsupported files."""
        self._unsupported += 1
        self.report_skipped()

    def __str__(self):
        return f"""
        COPIED: {self.copied}
        DUPLICATES: {self.duplicates}
        CONFLICTS: {self.conflicts}
        UNSUPPORTED: {self.unsupported}"""