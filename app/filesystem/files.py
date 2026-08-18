from pathlib import Path


# ---------------------------------------------------------
# NEXUS FILESYSTEM SANDBOX
# ---------------------------------------------------------

WORKSPACE = Path("/home/alpha/nexus/workspace").resolve()


# ---------------------------------------------------------
# Security
# ---------------------------------------------------------

def safe_path(path: str) -> Path:
    """
    Resolve a user-provided path and make sure it stays
    inside the NEXUS workspace.
    """

    requested = (WORKSPACE / path).resolve()

    try:
        requested.relative_to(WORKSPACE)
    except ValueError:
        raise PermissionError(
            "Access denied: path is outside the NEXUS workspace."
        )

    return requested


# ---------------------------------------------------------
# List files
# ---------------------------------------------------------

def list_files(path: str = "."):
    directory = safe_path(path)

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory not found: {path}"
        )

    if not directory.is_dir():
        raise NotADirectoryError(
            f"{path} is not a directory."
        )

    results = []

    for item in sorted(directory.iterdir()):
        relative = item.relative_to(WORKSPACE)

        if item.is_dir():
            results.append(f"[DIR]  {relative}")
        else:
            results.append(f"[FILE] {relative}")

    return results


# ---------------------------------------------------------
# Read file
# ---------------------------------------------------------

def read_file(path: str):
    file_path = safe_path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"{path} is not a file."
        )

    return file_path.read_text(
        encoding="utf-8"
    )


# ---------------------------------------------------------
# Create file
# ---------------------------------------------------------

def create_file(path: str, content: str):
    file_path = safe_path(path)

    if file_path.exists():
        raise FileExistsError(
            f"File already exists: {path}"
        )

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return file_path.relative_to(WORKSPACE)


# ---------------------------------------------------------
# Update file
# ---------------------------------------------------------

def update_file(path: str, content: str):
    file_path = safe_path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"{path} is not a file."
        )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return file_path.relative_to(WORKSPACE)


# ---------------------------------------------------------
# Delete file
# ---------------------------------------------------------

def delete_file(path: str):
    file_path = safe_path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"{path} is not a file."
        )

    file_path.unlink()

    return True


# ---------------------------------------------------------
# Search files
# ---------------------------------------------------------

def search_files(query: str):
    """
    Search text inside all files in the workspace.
    """

    if not query.strip():
        return []

    results = []

    for file_path in WORKSPACE.rglob("*"):

        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )
        except (UnicodeDecodeError, OSError):
            continue

        if query.lower() in content.lower():

            relative = file_path.relative_to(WORKSPACE)

            results.append(str(relative))

    return results
