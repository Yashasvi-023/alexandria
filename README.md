# Alexandria

**A local-first file intelligence system.**

Alexandria is an experimental Python project designed to help computers understand and organise their own filesystem.

The idea is simple: instead of manually navigating folders, remembering file locations, or searching through thousands of files, you should eventually be able to ask your computer what you're looking for and let it find the answer.

Alexandria aims to evolve from a filesystem discovery and retrieval system into an AI-powered personal knowledge assistant.

## The Vision

Alexandria is being developed around three core ideas:

- **Discovery:** Understand the structure and contents of the filesystem through metadata collection.
- **Memory:** Maintain a persistent, structured representation of discovered files and directories.
- **Intelligence:** Eventually use AI to interpret natural-language requests, reason over stored information, and help users interact with their filesystem.

The long-term goal is to build an assistant that understands the environment it operates in, rather than merely executing commands.

## Current Features

The project is currently in its foundational development stage.

### Filesystem Discovery
- Dynamically discover files within specified directories.
- Filter files by extension and size.
- Support recursive and non-recursive discovery.
- Exclude specified directories.
- Retrieve file metadata such as name, path, extension, size, and modification time.

### Directory Catalogue
- Discover directory structures recursively.
- Control scanning depth.
- Exclude selected directories.
- Record directory metadata and parent relationships.

### Persistent Storage
- SQLite-based metadata storage.
- Separate tables for files and directories.
- Unique filesystem paths to prevent duplicate records.
- Upsert operations to update existing metadata.

### Retrieval
- Search files by name or path.
- Filter files by extension.
- Retrieve files within a directory.
- Find the largest files.
- Navigate directory relationships, including parents, children, siblings, ancestors, and descendants.

## Architecture

Alexandria follows a modular architecture in which each component has a distinct responsibility.

```text
Alexandria/
│
├── collector/
│   ├── scanner.py
│   ├── discovery.py
│   ├── cli.py
│   ├── directory_resolver.py
│   ├── directory_catalogue.py
│   └── file_catalogue.py
│
├── storage/
│   ├── database.py
│   ├── retrieval.py
│   └── alexandria.db
│
├── intelligence/
│
├── interface/
│
└── README.md
```

**Collector:** Discovers files and directories and gathers filesystem metadata.

**Storage:** Maintains Alexandria's persistent SQLite database.

**Retrieval:** Provides functions to search and navigate the stored metadata.

**Intelligence:** Reserved for future AI-driven interpretation and reasoning.

**Interface:** Reserved for future user interaction.

## Technology Stack

- Python
- SQLite
- Standard Python filesystem libraries
- Argparse for command-line interfaces

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd Alexandria
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Initialize the database

```powershell
python -m storage.database
```

### 4. Catalogue files

Example:

```powershell
python -m collector.file_catalogue "$env:USERPROFILE\OneDrive\Desktop\Codes and Study\Projects\Alexandria" --exclude .git --exclude .venv --exclude __pycache__ --exclude node_modules
```

### 5. Catalogue directories

```powershell
python -m collector.directory_catalogue "$env:USERPROFILE" --max-depth 3 --exclude AppData
```

## Design Principles

Alexandria is being developed with a few important principles:

- **Local-first:** Filesystem discovery and metadata storage happen locally.
- **Read-only by default:** Discovery should not modify or delete user files.
- **Modularity:** Collection, storage, retrieval, and intelligence should remain separate responsibilities.
- **Controlled execution:** AI should interpret user intent, while Python handles validated operations.
- **Efficiency:** Prefer periodic scans over unnecessary continuous filesystem monitoring.
- **Transparency:** Alexandria should know what it has discovered and what it has not.

## Roadmap

- [x] Dynamic file discovery
- [x] Directory discovery and cataloguing
- [x] SQLite metadata storage
- [x] File and directory retrieval
- [ ] Catalogue synchronisation and stale-record reconciliation
- [ ] Improved filesystem scan tracking
- [ ] File content extraction
- [ ] Semantic indexing and retrieval
- [ ] LLM-powered natural-language interpretation
- [ ] Intelligent query resolution
- [ ] User-facing interface

## Project Status

**Early development.**

Alexandria is an evolving personal project. Its current implementation focuses on building a reliable filesystem knowledge foundation before introducing AI-driven capabilities.

## Philosophy

A computer contains an enormous amount of information, but much of it remains difficult to navigate and understand.

Alexandria explores the idea that a computer should gradually develop an understanding of its own environment, making information easier to discover, access, and reason about.

*The goal isn't to build another search bar. It's to build a system that understands what it's searching.*