# Architecture Documentation

This directory contains PlantUML diagrams documenting the Artifact Retrieval Service architecture.

## Diagrams

### 1. Architecture Diagram (`architecture.puml`)
High-level architecture showing:
- Subsystems (API, GitLab, Monitoring)
- Components and their relationships
- Data models
- External dependencies
- Data flow

**View:** Use a PlantUML viewer or render with:
```bash
# Online: https://www.plantuml.com/plantuml/uml/
# Or use VS Code extension: PlantUML
# Or use: java -jar plantuml.jar architecture.puml
```

### 2. Sequence Diagram (`sequence.puml`)
Detailed sequence diagram showing:
- Request flow from client to GitLab
- Error handling paths
- File download process
- Logging at each step

### 3. Component Diagram (`component.puml`)
Component-level view showing:
- Module dependencies
- Interface implementations
- External library dependencies
- File system interactions

### 4. Class Diagram (`class_diagram.puml`)
Python class structure showing:
- Class definitions and attributes
- Method signatures
- Interface implementations
- Relationships between classes

## Rendering PlantUML Diagrams

### Option 1: VS Code Extension
1. Install "PlantUML" extension in VS Code
2. Open `.puml` file
3. Press `Alt+D` to preview

### Option 2: Online Viewer
1. Copy PlantUML code
2. Visit: https://www.plantuml.com/plantuml/uml/
3. Paste and view

### Option 3: Command Line
```bash
# Install PlantUML (requires Java)
# Download from: https://plantuml.com/download

# Render to PNG
java -jar plantuml.jar architecture.puml

# Render to SVG
java -jar plantuml.jar -tsvg architecture.puml
```

### Option 4: GitHub/GitLab
Both GitHub and GitLab can render PlantUML diagrams directly in markdown:
````markdown
```plantuml
@startuml
... your diagram code ...
@enduml
```
````

## Architecture Overview

The service follows a clean architecture with three main subsystems:

1. **ApiSubsystem**: Handles HTTP requests, validation, and mapping
2. **GitLabSubsystem**: Manages GitLab API communication and file downloads
3. **MonitoringSubsystem**: Provides logging and health checks

All subsystems interact through well-defined interfaces and dependency injection.

