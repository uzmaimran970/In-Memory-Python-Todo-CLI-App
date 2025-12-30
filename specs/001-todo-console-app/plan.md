# Implementation Plan: In-Memory Python Todo Console Application

**Branch**: `001-todo-console-app` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)

---

## Summary

This plan outlines the implementation of a console-based todo application in Python 3.13+ with in-memory storage. The application provides 5 core operations (Add, View, Update, Delete, Toggle Completion) through a menu-driven CLI interface. The architecture follows a three-layer pattern (Data, Business Logic, Presentation) to ensure clean separation of concerns and testability.

**Key Decisions**:
- **Task Model**: Dataclass for type safety and validation
- **ID Generation**: Auto-incrementing integer counter (simple, user-friendly)
- **Storage**: Dictionary for O(1) lookups by task ID
- **Architecture**: Three-layer separation (models, services, cli)
- **Error Handling**: Typed exceptions with user-friendly messages

**Technical Approach** (from research):
- Dataclasses for Task representation (type safety, validation)
- Three-layer architecture for separation of concerns
- Exception-based error handling
- Menu-driven CLI for user-friendly interaction

---

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Standard library only (dataclasses, typing)
**Storage**: In-memory dictionary (`dict[int, Task]`)
**Testing**: Manual acceptance testing (unit tests optional)
**Target Platform**: Any platform with Python 3.13+ (Linux, macOS, Windows)
**Project Type**: Single console application
**Performance Goals**: Instant response for all operations, handle 100+ tasks
**Constraints**:
- No persistence (in-memory only)
- No external dependencies beyond standard library
- Single-user, single-threaded
- Must handle 100 tasks without degradation (SC-004)
**Scale/Scope**:
- 5 core operations
- ~500 lines of code total
- 4 Python modules (task.py, todo_manager.py, console.py, main.py)
- Hackathon Phase 1 scope

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Check 1: Spec-First Development ✓

**Requirement**: All features start with specification, no implementation before spec approval.

**Status**: **PASS** - Specification created via `/sp.specify` and validated before planning.

**Evidence**:
- `specs/001-todo-console-app/spec.md` exists with 4 user stories and 15 functional requirements
- Specification validation checklist completed (all items passed)
- Planning initiated only after spec approval

---

### Check 2: Separation of Concerns ✓

**Requirement**: Business logic must be independent of I/O, UI, and infrastructure.

**Status**: **PASS** - Three-layer architecture ensures clean separation.

**Evidence**:
- **Data Layer** (`models/task.py`): Pure data structures, no I/O
- **Business Logic Layer** (`services/todo_manager.py`): CRUD operations, no console I/O
- **Presentation Layer** (`cli/console.py`): Menu and user interaction, calls business logic
- TodoManager has zero `input()` or `print()` calls (verified in contract)

---

### Check 3: Simplicity & YAGNI ✓

**Requirement**: Start simple, avoid over-engineering, no features beyond requirements.

**Status**: **PASS** - Minimal design with no extra features.

**Evidence**:
- No features beyond spec requirements (no search, filters, priorities, etc.)
- Standard library only (no external dependencies)
- Simple dict storage (not database, not ORM)
- Auto-increment IDs (not UUID, not hash-based)
- No unnecessary patterns (no repository, no DI, no event bus)

---

### Check 4: Deterministic Behavior ✓

**Requirement**: Given same inputs, produce same outputs. Minimize randomness.

**Status**: **PASS** - All operations are deterministic.

**Evidence**:
- Task IDs are sequential and predictable (1, 2, 3, ...)
- No timestamps, no random values, no UUIDs
- Same operations produce same results (add → same ID, toggle → predictable state change)
- In-memory state fully controlled (no external state)

---

### Check 5: Error Handling ✓

**Requirement**: Graceful error handling with clear user messages.

**Status**: **PASS** - Exception-based error handling with typed exceptions.

**Evidence**:
- Typed exceptions (`TaskNotFoundError`, `InvalidInputError`)
- All TodoManager operations document exception conditions
- CLI layer catches and displays user-friendly messages
- No silent failures (all errors surfaced)

---

### Post-Phase 1 Constitution Re-Check ✓

**Status**: All gates still PASS after design phase.

**Changes**:
- No constitution violations introduced during design
- All decisions align with simplicity and separation principles
- Contracts formalized without adding complexity

---

## Complexity Tracking

**No violations**: All design decisions comply with constitution principles. No complexity justification needed.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-console-app/
├── spec.md                         # Feature specification (created via /sp.specify)
├── plan.md                         # This file (implementation plan)
├── research.md                     # Phase 0: Architecture decisions and rationale
├── data-model.md                   # Phase 1: Entity definitions and state management
├── quickstart.md                   # Phase 1: Developer quick-start guide
├── contracts/                      # Phase 1: Behavioral contracts
│   ├── todo-manager-contract.md    # TodoManager method specifications
│   └── cli-interface-contract.md   # CLI user experience specifications
└── checklists/                     # Created during /sp.specify
    └── requirements.md             # Specification quality validation
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── task.py                     # Task dataclass, exception classes
├── services/
│   ├── __init__.py
│   └── todo_manager.py             # TodoManager business logic (CRUD operations)
├── cli/
│   ├── __init__.py
│   └── console.py                  # CLI menu, input handling, output formatting
└── main.py                         # Application entry point

tests/                              # Optional (not required for Phase 1)
├── __init__.py
├── test_task.py                    # Task model unit tests
├── test_todo_manager.py            # TodoManager unit tests
└── test_cli.py                     # CLI integration tests
```

**Structure Decision**:

Selected **Option 1: Single project** structure because:
- This is a single console application (not web, not mobile)
- No frontend/backend separation needed
- Separation achieved through module organization (models, services, cli)
- Keeps structure simple and aligned with hackathon scope

**Module Responsibilities**:

| Module | Responsibility | No Console I/O | No Business Logic |
|--------|----------------|----------------|-------------------|
| `models/task.py` | Data structures, exceptions | ✓ | ✓ |
| `services/todo_manager.py` | Business logic, state management | ✓ | N/A (this IS business logic) |
| `cli/console.py` | User interaction, formatting | N/A (this IS I/O) | ✓ |
| `main.py` | Entry point, initialization | ✓ | ✓ |

---

## Architecture Diagram

### High-Level Component View

```
┌─────────────────────────────────────────────────────────────┐
│                        User (Terminal)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Console I/O (input/output)
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   CLI Layer (console.py)                     │
│  - Display menu                                              │
│  - Get user input                                            │
│  - Format output                                             │
│  - Handle errors (catch exceptions, display messages)        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Method calls (add_task, get_all_tasks, etc.)
                            │ Returns: Task objects, IDs, exceptions
                            │
┌───────────────────────────▼─────────────────────────────────┐
│            Business Logic Layer (todo_manager.py)            │
│  - TodoManager class                                         │
│  - CRUD operations (add, get, update, delete, toggle)       │
│  - Validation logic                                          │
│  - State management (_tasks dict, _next_id counter)          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Creates/reads Task objects
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                 Data Layer (task.py)                         │
│  - Task dataclass (id, title, description, completed)        │
│  - Exception classes (TodoError, TaskNotFoundError, etc.)    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Example: Add Task

```
User Input: "1" (menu choice)
    ↓
[CLI] display_menu() → handle_add_task()
    ↓
User Input: "Buy milk" (title), "From store" (description)
    ↓
[CLI] validate inputs, call manager.add_task("Buy milk", "From store")
    ↓
[Business Logic] TodoManager.add_task()
    ├─ Validate title (non-empty, ≤200 chars)
    ├─ Validate description (≤1000 chars)
    ├─ Generate ID (self._next_id = 1)
    ├─ Create Task(1, "Buy milk", "From store", False)
    ├─ Store in self._tasks[1]
    ├─ Increment self._next_id to 2
    └─ Return 1 (new task ID)
    ↓
[CLI] Display "✓ Task added successfully (ID: 1)"
    ↓
[CLI] Return to menu
```

---

## Implementation Strategy

### Phase-by-Phase Breakdown

#### Phase 1: Specification Confirmation ✓ COMPLETED

**Goal**: Validate specification is clear and complete.

**Activities**:
- ✓ Review `specs/001-todo-console-app/spec.md`
- ✓ Verify 4 user stories are well-defined and prioritized
- ✓ Verify 15 functional requirements are unambiguous
- ✓ Verify 10 success criteria are measurable
- ✓ Validate against constitution principles

**Deliverables**:
- ✓ Spec validation complete (via `/sp.specify`)
- ✓ No [NEEDS CLARIFICATION] markers in spec

**Acceptance Criteria**:
- ✓ All user stories have acceptance scenarios
- ✓ All edge cases identified
- ✓ All assumptions documented

---

#### Phase 2: Core Data Model ⏭ NEXT

**Goal**: Implement Task dataclass and exception hierarchy.

**Activities**:
1. Create `src/models/` directory
2. Implement `task.py`:
   - Task dataclass with fields: id, title, description, completed
   - `__post_init__` validation (title non-empty, length limits)
   - TodoError base exception
   - TaskNotFoundError exception
   - InvalidInputError exception

**Deliverables**:
- `src/models/__init__.py` (exports Task and exceptions)
- `src/models/task.py` (Task dataclass, exceptions)

**Acceptance Criteria**:
- [ ] Task can be instantiated with valid data
- [ ] Task raises ValueError for empty title
- [ ] Task raises ValueError for title >200 chars
- [ ] Task raises ValueError for description >1000 chars
- [ ] All exceptions inherit from TodoError
- [ ] Type hints on all attributes

**Test**:
```python
from src.models.task import Task, TodoError

# Valid task
t1 = Task(1, "Test", "Desc", False)
assert t1.id == 1

# Invalid task
try:
    t2 = Task(2, "", "Desc", False)
except ValueError:
    print("Validation works!")
```

**Estimated Effort**: 30 minutes

---

#### Phase 3: Business Logic

**Goal**: Implement TodoManager with all CRUD operations.

**Activities**:
1. Create `src/services/` directory
2. Implement `todo_manager.py`:
   - TodoManager class with `__init__`
   - `_tasks` dict and `_next_id` counter
   - `add_task(title, description)` → int
   - `get_task(task_id)` → Task
   - `get_all_tasks()` → list[Task]
   - `update_task(task_id, title?, description?)` → None
   - `delete_task(task_id)` → None
   - `toggle_completion(task_id)` → bool
   - `task_count()` → int

**Deliverables**:
- `src/services/__init__.py` (exports TodoManager)
- `src/services/todo_manager.py` (TodoManager implementation)

**Acceptance Criteria**:
- [ ] All 8 methods implemented per contract specification
- [ ] IDs start at 1 and auto-increment
- [ ] IDs never reused (even after deletion)
- [ ] TaskNotFoundError raised for invalid IDs
- [ ] InvalidInputError raised for validation failures
- [ ] No console I/O (`input()` or `print()`) in TodoManager
- [ ] Type hints on all method signatures
- [ ] Docstrings on all public methods

**Reference**: `specs/001-todo-console-app/contracts/todo-manager-contract.md`

**Test** (interactive Python):
```python
from src.services.todo_manager import TodoManager
from src.models.task import TaskNotFoundError

m = TodoManager()
id1 = m.add_task("Task 1", "Desc 1")
id2 = m.add_task("Task 2", "Desc 2")
print(m.get_all_tasks())  # 2 tasks
m.toggle_completion(id1)
print(m.get_task(id1).completed)  # True
m.delete_task(id2)
print(m.task_count())  # 1
```

**Estimated Effort**: 1.5 hours

---

#### Phase 4: CLI Interaction Layer

**Goal**: Implement console interface with menu and operation handlers.

**Activities**:
1. Create `src/cli/` directory
2. Implement `console.py`:
   - `display_menu()` → None
   - `get_menu_choice()` → int
   - `get_integer_input(prompt)` → int (with validation loop)
   - `handle_add_task(manager)` → None
   - `handle_view_tasks(manager)` → None
   - `handle_update_task(manager)` → None
   - `handle_delete_task(manager)` → None
   - `handle_toggle_completion(manager)` → None
   - `run()` → None (main application loop)

**Deliverables**:
- `src/cli/__init__.py` (exports run)
- `src/cli/console.py` (CLI implementation)

**Acceptance Criteria**:
- [ ] Menu displays with all 6 options (5 operations + Exit)
- [ ] All handlers implemented per CLI contract
- [ ] Exceptions caught and converted to user-friendly messages
- [ ] Invalid inputs handled gracefully (no crashes)
- [ ] Application exits cleanly on option 6
- [ ] Type hints on all functions
- [ ] Docstrings on all public functions

**Reference**: `specs/001-todo-console-app/contracts/cli-interface-contract.md`

**Test** (manual):
```bash
python -c "from src.cli.console import run; run()"
```

**Estimated Effort**: 2 hours

---

#### Phase 5: Integration and Manual Validation

**Goal**: Wire all layers together and validate against acceptance scenarios.

**Activities**:
1. Create `src/main.py`:
   ```python
   from src.cli.console import run

   if __name__ == "__main__":
       run()
   ```
2. Manual testing of all acceptance scenarios from spec
3. Verify all success criteria (SC-001 through SC-010)
4. Edge case testing (empty inputs, invalid IDs, etc.)

**Deliverables**:
- `src/main.py` (entry point)
- Completed manual test results (documented in testing log or PHR)

**Acceptance Criteria**:
- [ ] All user stories' acceptance scenarios pass
- [ ] All 10 success criteria verified
- [ ] Edge cases handled correctly
- [ ] No crashes on invalid input
- [ ] Data lost on restart (in-memory requirement)
- [ ] Application runs from command line with `python src/main.py`

**Manual Test Scenarios**:
1. **User Story 1**: Add tasks, view list
2. **User Story 2**: Toggle completion (incomplete → complete → incomplete)
3. **User Story 3**: Update task title and description
4. **User Story 4**: Delete task, verify removal
5. **Edge Cases**: Empty title, invalid ID, non-integer input

**Reference**: `specs/001-todo-console-app/spec.md` (Acceptance Scenarios sections)

**Estimated Effort**: 1 hour

---

### Total Estimated Effort

| Phase | Effort | Status |
|-------|--------|--------|
| Phase 1: Spec Confirmation | 30 min | ✓ COMPLETED |
| Phase 2: Data Model | 30 min | ⏭ NEXT |
| Phase 3: Business Logic | 1.5 hours | Pending |
| Phase 4: CLI Layer | 2 hours | Pending |
| Phase 5: Integration & Testing | 1 hour | Pending |
| **Total** | **~5.5 hours** | **Phase 1 complete** |

---

## Testing & Validation Strategy

### Manual Test Cases

Derived from spec acceptance scenarios (User Stories 1-4):

| Test ID | Scenario | Steps | Expected Result |
|---------|----------|-------|----------------|
| TC-01 | Add task (valid) | Add "Buy groceries" / "Milk, eggs, bread" | Task added with ID 1, success message |
| TC-02 | Add task (empty title) | Add "" / "Description" | Error message, re-prompt |
| TC-03 | View tasks (empty) | Start app, select View | "No tasks found" message |
| TC-04 | View tasks (multiple) | Add 3 tasks, select View | All 3 tasks displayed with details |
| TC-05 | Toggle completion | Add task, toggle ID 1 | Status changes to Complete |
| TC-06 | Toggle twice | Add task, toggle twice | Status returns to Incomplete |
| TC-07 | Update title | Add task, update title to "New Title" | Title changes, description unchanged |
| TC-08 | Update description | Add task, update description only | Description changes, title unchanged |
| TC-09 | Update both fields | Add task, update both | Both change |
| TC-10 | Update non-existent | Try to update ID 999 | "Task not found" error |
| TC-11 | Delete task | Add 3 tasks, delete ID 2 | Only IDs 1 and 3 remain |
| TC-12 | Delete non-existent | Try to delete ID 999 | "Task not found" error |
| TC-13 | Invalid menu choice | Enter 9 at menu | Error message, menu redisplays |
| TC-14 | Non-integer ID | Enter "abc" for task ID | Error message, re-prompt |
| TC-15 | Exit application | Select option 6 | Goodbye message, clean exit |

**Total**: 15 manual test cases

### Success Criteria Validation

Map success criteria to test approach:

| Criteria | Test Method | Acceptance |
|----------|-------------|------------|
| SC-001: Add/view in ≤3 selections | Manual test TC-01, TC-04 | User can add and see task in 3 steps |
| SC-002: View shows all details | Manual test TC-04 | All fields (ID, title, desc, status) visible |
| SC-003: 5 operations without errors | Manual tests TC-01, TC-04, TC-07, TC-11, TC-05 | All operations complete successfully |
| SC-004: Handle 100 tasks | Script: Add 100 tasks, view list | No performance degradation |
| SC-005: Clear error messages | Manual tests TC-02, TC-10, TC-12, TC-14 | Errors user-friendly, actionable |
| SC-006: 100% unique IDs | Script: Add 100 tasks, verify IDs | All IDs unique, sequential |
| SC-007: Toggle works correctly | Manual test TC-05, TC-06 | Status changes as expected |
| SC-008: Data lost on restart | Restart app after adding tasks | Task list empty on startup |
| SC-009: Separation verified | Code review | No I/O in TodoManager, no logic in CLI |
| SC-010: Clean start/exit | Manual test TC-15 | No errors on startup or exit |

### Unit Testing (Optional)

If time permits, implement unit tests for TodoManager:

**Test Coverage Areas**:
- `test_add_task`: Valid task, empty title, title too long, description too long
- `test_get_task`: Existing task, non-existent task
- `test_get_all_tasks`: Empty, multiple tasks, sorted order
- `test_update_task`: Title only, description only, both, neither, not found
- `test_delete_task`: Existing task, non-existent task, double delete
- `test_toggle_completion`: False→True, True→False, not found
- `test_task_count`: After add, after delete

**Framework**: pytest (if using unit tests)

**Run**: `pytest tests/`

**Note**: Unit tests are NOT required for Phase 1 hackathon scope. Manual testing is sufficient per spec.

---

## Architectural Decision Records (ADRs)

### Significant Decisions Requiring Documentation

Based on research phase, the following decisions meet ADR criteria (Impact + Alternatives + Scope):

1. **Task Data Structure: Dataclass vs Dictionary**
   - Impact: Affects type safety, validation, and developer experience
   - Alternatives: Dataclass, plain dict, NamedTuple, custom class
   - Scope: All task-related code
   - **Recommendation**: Document in ADR

2. **ID Generation Strategy: Auto-increment vs UUID**
   - Impact: User experience, simplicity, testing
   - Alternatives: Auto-increment int, UUID, hash-based, timestamp
   - Scope: Task creation, user references (update, delete, toggle)
   - **Recommendation**: Document in ADR

3. **Architecture Pattern: 3-Layer Separation**
   - Impact: Code organization, testability, maintainability
   - Alternatives: Single file, MVC, hexagonal
   - Scope: Entire application structure
   - **Recommendation**: Document in ADR

### ADR Suggestion Timing

**When**: After Phase 1 design is complete (NOW) or after implementation (if user prefers post-implementation documentation).

**Suggested ADRs**:
1. **ADR-001: Use Dataclass for Task Model**
   - Decision: Task represented as Python dataclass
   - Rationale: Type safety, validation, readability
   - Tradeoffs: Slightly more boilerplate than dict, but better safety

2. **ADR-002: Use Auto-Incrementing Integer IDs**
   - Decision: Task IDs are sequential integers starting from 1
   - Rationale: Simple, user-friendly, deterministic
   - Tradeoffs: Not globally unique (fine for in-memory), simpler than UUID

3. **ADR-003: Three-Layer Architecture (Data, Logic, CLI)**
   - Decision: Separate models, services, and CLI layers
   - Rationale: Separation of concerns, testability, spec requirement (FR-012)
   - Tradeoffs: More files than monolith, but cleaner boundaries

**To Document**: Run `/sp.adr <title>` for each significant decision after user consent.

📋 **Architectural decisions detected**:
- Task data structure (dataclass vs dictionary)
- ID generation strategy (auto-increment vs UUID)
- Architecture pattern (3-layer separation)

**Document reasoning and tradeoffs?** Run `/sp.adr` after Phase 1 completion to create ADRs for these decisions.

---

## Risk Analysis and Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|-----------|--------|-------------------|
| **Scope Creep** (adding features not in spec) | Medium | Medium | Strict adherence to FR-001 through FR-015; code review against spec before finalizing |
| **Mixing Concerns** (I/O in business logic) | Medium | Medium | Code review to verify TodoManager has no `input()`/`print()`; follow contracts strictly |
| **Poor Error Messages** (technical jargon) | Low | Low | Test all error scenarios manually; ensure messages are user-friendly per CLI contract |
| **ID Collision** (unlikely with counter) | Very Low | Low | Use simple counter pattern; add assertion in tests to verify uniqueness |
| **Performance Issues** (with 100 tasks) | Very Low | Low | Dict lookup is O(1); 100 tasks is trivial; verify SC-004 with manual test |
| **Type Errors** (no type checking) | Low | Low | Run mypy if available; use type hints throughout |

**Overall Risk Level**: LOW - Simple application with well-defined scope and proven patterns.

---

## Development Workflow with Claude Code + Spec-Kit Plus

### Step-by-Step Flow

#### 1. Planning Phase (Current)
```bash
/sp.plan [planning requirements]
```
**Output**: This document + research.md + data-model.md + contracts/ + quickstart.md

#### 2. Task Generation (Next)
```bash
/sp.tasks
```
**Output**: `specs/001-todo-console-app/tasks.md` with detailed, prioritized implementation tasks

#### 3. Implementation Phase
Use Claude Code to implement tasks incrementally:
```
"Implement Phase 2: Core Data Model (task.py with Task dataclass and exceptions)"
"Implement Phase 3: Business Logic (TodoManager with all CRUD operations)"
"Implement Phase 4: CLI Layer (console.py with menu and handlers)"
"Integrate all layers in main.py and test"
```

#### 4. Validation Phase
- Run manual test scenarios
- Verify all success criteria
- Code review against contracts

#### 5. Documentation Phase
- Create Prompt History Records for significant work
- Create ADRs for architectural decisions (if desired)
- Update README.md with user instructions

#### 6. Commit & PR
```bash
/sp.git.commit_pr
```
**Output**: Git commit + GitHub PR for Phase 1 completion

---

## Next Steps After Planning

1. **Generate Tasks**: Run `/sp.tasks` to create detailed task breakdown
2. **Review Plan**: Ensure plan aligns with your expectations
3. **Start Implementation**: Begin with Phase 2 (Data Model)
4. **Iterate**: Implement → Test → Validate → Document
5. **Finalize**: Manual testing → ADRs (optional) → Commit

---

## Appendix: File Checklist

### Planning Artifacts (Created)
- [x] `specs/001-todo-console-app/spec.md` (from `/sp.specify`)
- [x] `specs/001-todo-console-app/plan.md` (this file)
- [x] `specs/001-todo-console-app/research.md` (Phase 0 output)
- [x] `specs/001-todo-console-app/data-model.md` (Phase 1 output)
- [x] `specs/001-todo-console-app/quickstart.md` (Phase 1 output)
- [x] `specs/001-todo-console-app/contracts/todo-manager-contract.md` (Phase 1 output)
- [x] `specs/001-todo-console-app/contracts/cli-interface-contract.md` (Phase 1 output)

### Source Code (To Be Created)
- [ ] `src/__init__.py`
- [ ] `src/models/__init__.py`
- [ ] `src/models/task.py`
- [ ] `src/services/__init__.py`
- [ ] `src/services/todo_manager.py`
- [ ] `src/cli/__init__.py`
- [ ] `src/cli/console.py`
- [ ] `src/main.py`

### Optional Files
- [ ] `tests/test_task.py`
- [ ] `tests/test_todo_manager.py`
- [ ] `tests/test_cli.py`
- [ ] `README.md` (user-facing documentation)
- [ ] `history/adr/001-dataclass-task-model.md`
- [ ] `history/adr/002-auto-increment-ids.md`
- [ ] `history/adr/003-three-layer-architecture.md`

---

## Summary

**Planning Complete**: All Phase 0 (Research) and Phase 1 (Design) artifacts generated.

**Ready for**: Task generation (`/sp.tasks`) and implementation.

**Key Deliverables**:
- Architecture decisions documented in `research.md`
- Data model specified in `data-model.md`
- Behavioral contracts in `contracts/`
- Quick-start guide in `quickstart.md`
- Implementation strategy in this file (`plan.md`)

**Estimated Implementation Time**: ~5.5 hours (data model → business logic → CLI → integration)

**Next Command**: `/sp.tasks` to generate detailed implementation tasks.

---

**Version**: 1.0 | **Status**: Planning Complete | **Phase**: Ready for Task Generation
