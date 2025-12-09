# Data Model: Robotics Textbook Content

**Date**: 2025-12-08

This document outlines the data model for the content of the "Physical AI & Humanoid Robotics" textbook. As this is a content-driven project, the "data" is the textual and visual information that makes up the book, structured for Docusaurus.

## Entity Relationship Diagram (Conceptual)

```
[Textbook]
    |
    +-- [Module] (1..4)
           |
           +-- [Chapter] (1..2)
                  |
                  +-- [Subchapter] (1..*)
                         |
                         +-- [ContentBlock] (1..*)
```

## Entity Definitions

### 1. Textbook

The top-level container for the entire work.

-   **Attributes**:
    -   `title`: (string) "Physical AI & Humanoid Robotics"
    -   `language`: (enum) 'en' | 'ur'

### 2. Module

A major thematic section of the textbook. There are exactly 4 modules.

-   **Attributes**:
    -   `title`: (string) e.g., "The Robotic Nervous System (ROS 2)"
    -   `wordCountTarget`: (integer) ~4000
-   **Relationships**:
    -   Has many `Chapters`.

### 3. Chapter

A division within a `Module`.

-   **Attributes**:
    -   `title`: (string) e.g., "Understanding ROS 2 Nodes"
-   **Relationships**:
    -   Belongs to one `Module`.
    -   Has many `Subchapters`.

### 4. Subchapter

The most granular level of content organization, containing the actual learning material.

-   **Attributes**:
    -   `title`: (string) e.g., "Creating Your First Python Node"
-   **Relationships**:
    -   Belongs to one `Chapter`.
    -   Has many `ContentBlocks`.

### 5. ContentBlock

A discrete piece of content within a `Subchapter`. Each `Subchapter` is composed of an ordered collection of these blocks.

-   **Attributes**:
    -   `type`: (enum) [ 'Introduction', 'Description', 'CodeExample', 'DiagramPlaceholder', 'Quiz', 'Glossary', 'References', 'History' ]
    -   `content`: (string) The actual text, code, or Markdown for the block.
-   **Validation Rules**:
    -   `CodeExample` blocks must specify the language (e.g., Python, C++, C#).
    -   `DiagramPlaceholder` blocks must use Markdown image syntax with descriptive alt text (e.g., `![Diagram: A simple ROS 2 computation graph with two nodes and one topic.]`).
    -   All required content blocks must be present in each subchapter as per the feature specification.
