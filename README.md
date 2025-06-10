# SpiceflowNavigator-Pipeline

**Pipeline Agent** for SpiceflowNavigator

## Quick Start

```bash
# Clone with submodules (for agents)
git clone --recursive git@github.com:pa5tabear/SpiceflowNavigator-Pipeline.git
cd SpiceflowNavigator-Pipeline

# Install dependencies
make install

# Run tests
make test
```

## Agent Responsibilities

- 🎯 **End-to-end workflow orchestration**
- 🖥️ **CLI interface and job coordination**
- 🔗 **Integration between all agents**
- 📋 **Main entry point for SpiceflowNavigator**

## Development Commands

```bash
make help          # Show all commands
make test          # Run tests
make install       # Install dependencies  
make dev           # Start development server
make clean         # Clean temporary files
```


## Optional CommonUtils Package

The pipeline can run without the shared utilities package. If you need those
extras, clone the [CommonUtils](git@github.com:pa5tabear/SpiceflowNavigator-CommonUtils) repository
and install it manually:

```bash
git clone git@github.com:pa5tabear/SpiceflowNavigator-CommonUtils.git
pip install -e SpiceflowNavigator-CommonUtils/
```

## Related Repositories

- [Pipeline Agent](git@github.com:pa5tabear/SpiceflowNavigator-Pipeline) - End-to-end orchestration
- [Ingest Agent](git@github.com:pa5tabear/SpiceflowNavigator-Ingest) - RSS + transcription
- [Strategy Agent](git@github.com:pa5tabear/SpiceflowNavigator-Strategy) - Analysis + scoring
- [UI Agent](git@github.com:pa5tabear/SpiceflowNavigator-UI) - User interface
- [CommonUtils](git@github.com:pa5tabear/SpiceflowNavigator-CommonUtils) - Shared utilities

## Architecture

This repository is part of SpiceflowNavigator's **4-Agent Architecture**:

```
Pipeline ←→ Ingest
    ↓         ↓
Strategy ←→ CommonUtils ←→ UI
```

Each agent operates independently while sharing common utilities.

---
*Part of the SpiceflowNavigator 4-Agent Architecture*
