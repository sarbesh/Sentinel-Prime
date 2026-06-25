# Database Strategy Decision for SENTINEL PRIME

## Current Strategy
- Primary Database: PostgreSQL with pgvector extension (for main data and vector storage)
- Secondary/Local Storage: SQLite (for mobile/offline/local storage)

## Evaluation
We evaluated the option of migrating to a single PostgreSQL instance for both primary and local storage.

### Pros of Single PostgreSQL Instance:
   - Reduced operational complexity (one database system)
   - Uniform data management and backup procedures
   - Potential for simpler architecture

### Cons of Single PostgreSQL Instance:
   - Overhead for lightweight/local use cases (especially on mobile devices)
   - Loss of offline capabilities that SQLite provides for mobile applications
   - Increased resource consumption for edge/local storage
   - SQLite is optimized for embedded, zero-administration scenarios

## Decision
**KEEP CURRENT STRATEGY** (separate PostgreSQL+pgvector for primary/vector data and SQLite for local/storage)

## Reasoning
The current strategy aligns with the strengths of each database:
   - PostgreSQL with pgvector provides robust, ACID-compliant storage with vector capabilities, ideal for the central server handling AI/embedding workloads.
   - SQLite is ideal for mobile/local storage due to its zero-configuration, file-based nature, and support for offline use.

Migrating to a single PostgreSQL instance would:
   - Increase complexity for mobile/edge devices (requiring a PostgreSQL client and connection to a central server for local storage)
   - Eliminate the ability to work offline with local data on mobile devices
   - Potentially increase costs and resource usage for lightweight local storage scenarios

Therefore, we recommend keeping the current separate database strategy.

## When to Re-evaluate
Consider revisiting this decision if:
   - The application's local storage requirements change significantly (e.g., need for stronger consistency or complex queries on local data)
   - A lightweight, embedded alternative to PostgreSQL emerges that better fits the local storage use case
   - Operational overhead of managing two databases becomes a significant burden and the local data volume justifies centralizing everything in PostgreSQL.