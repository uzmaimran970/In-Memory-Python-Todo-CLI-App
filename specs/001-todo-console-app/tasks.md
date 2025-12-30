# Tasks: In-Memory Python Todo Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Manual acceptance testing only (no automated tests for Phase 1 hackathon scope)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths: `src/models/`, `src/services/`, `src/cli/`, `src/main.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: src/, src/models/, src/services/, src/cli/
- [ ] T002 [P] Create all __init__.py files: src/__init__.py, src/models/__init__.py, src/services/__init__.py, src/cli/__init__.py
- [ ] T003 [P] Verify Python 3.13+ installation and type hint support

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data layer and exceptions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Define TodoError base exception class in src/models/task.py
- [ ] T005 [P] Define TaskNotFoundError exception class in src/models/task.py
- [ ] T006 [P] Define InvalidInputError exception class in src/models/task.py
- [ ] T007 Create Task dataclass with fields (id: int, title: str, description: str, completed: bool = False) in src/models/task.py
- [ ] T008 Implement Task.__post_init__ validation (ID > 0, title non-empty, title ≤200 chars, description ≤1000 chars) in src/models/task.py
- [ ] T009 Export Task and all exceptions in src/models/__init__.py

**Checkpoint**: Foundation ready - all user stories can now reference Task and exceptions

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks with title/description and view the complete task list

**Independent Test**: Add multiple tasks through console menu, view list showing all tasks with ID/title/description/status

### Implementation for User Story 1

**Business Logic**:
- [ ] T010 [P] [US1] Create TodoManager class with __init__ (_tasks: dict[int, Task], _next_id: int = 1) in src/services/todo_manager.py
- [ ] T011 [P] [US1] Implement TodoManager.add_task(title: str, description: str = "") -> int with validation in src/services/todo_manager.py
- [ ] T012 [P] [US1] Implement TodoManager.get_all_tasks() -> list[Task] with ID sorting in src/services/todo_manager.py
- [ ] T013 [P] [US1] Implement TodoManager.task_count() -> int in src/services/todo_manager.py
- [ ] T014 [US1] Export TodoManager in src/services/__init__.py

**CLI Layer**:
- [ ] T015 [P] [US1] Create display_menu() function showing all 6 menu options in src/cli/console.py
- [ ] T016 [P] [US1] Create get_menu_choice() -> int function with input validation loop in src/cli/console.py
- [ ] T017 [P] [US1] Create get_integer_input(prompt: str) -> int helper with error handling in src/cli/console.py
- [ ] T018 [US1] Implement handle_add_task(manager: TodoManager) function with title/description prompts and error handling in src/cli/console.py
- [ ] T019 [US1] Implement handle_view_tasks(manager: TodoManager) function formatting tasks or "No tasks found" message in src/cli/console.py
- [ ] T020 [US1] Create run() function with main loop (menu → choice → dispatch → repeat) and TodoManager initialization in src/cli/console.py
- [ ] T021 [US1] Export run in src/cli/__init__.py

**Application Entry Point**:
- [ ] T022 [US1] Create src/main.py importing and calling run() from cli module

**Manual Validation for User Story 1**:
- [ ] T023 [US1] Test: Start app, add task "Buy groceries" / "Milk, eggs, bread" → verify success message with ID 1
- [ ] T024 [US1] Test: Add 3 tasks, select View → verify all 3 tasks display with ID, title, description, incomplete status
- [ ] T025 [US1] Test: Start app, select View → verify "No tasks found" message
- [ ] T026 [US1] Test: Try to add task with empty title → verify error message and re-prompt

**Checkpoint**: User Story 1 complete - Users can add and view tasks (MVP functional!)

---

## Phase 4: User Story 2 - Mark Tasks Complete or Incomplete (Priority: P2)

**Goal**: Users can toggle task completion status to track progress

**Independent Test**: Create tasks, toggle completion by ID, view list showing updated statuses

### Implementation for User Story 2

**Business Logic**:
- [ ] T027 [P] [US2] Implement TodoManager.get_task(task_id: int) -> Task with TaskNotFoundError in src/services/todo_manager.py
- [ ] T028 [P] [US2] Implement TodoManager.toggle_completion(task_id: int) -> bool with TaskNotFoundError in src/services/todo_manager.py

**CLI Layer**:
- [ ] T029 [US2] Implement handle_toggle_completion(manager: TodoManager) function with ID prompt and status display in src/cli/console.py

**Manual Validation for User Story 2**:
- [ ] T030 [US2] Test: Add task, toggle ID 1 → verify "Task 1 marked as Complete" message
- [ ] T031 [US2] Test: Toggle same task again → verify "Task 1 marked as Incomplete" message
- [ ] T032 [US2] Test: View tasks after toggle → verify status shows "Complete ✓" or "Incomplete"
- [ ] T033 [US2] Test: Try to toggle non-existent ID 999 → verify "Task not found" error
- [ ] T034 [US2] Test: Try to toggle with non-integer input "abc" → verify error message

**Checkpoint**: User Stories 1 AND 2 complete - Users can create, view, and complete tasks

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Users can edit task title and description to correct mistakes or update information

**Independent Test**: Create task, update title only / description only / both fields, verify changes

### Implementation for User Story 3

**Business Logic**:
- [ ] T035 [US3] Implement TodoManager.update_task(task_id: int, title: str | None = None, description: str | None = None) with validation and TaskNotFoundError in src/services/todo_manager.py

**CLI Layer**:
- [ ] T036 [US3] Implement handle_update_task(manager: TodoManager) function with ID prompt, optional title/description inputs (Enter to skip), and error handling in src/cli/console.py

**Manual Validation for User Story 3**:
- [ ] T037 [US3] Test: Add task, update title to "New Title" (skip description) → verify title changes, description unchanged
- [ ] T038 [US3] Test: Add task, update description only (skip title) → verify description changes, title unchanged
- [ ] T039 [US3] Test: Add task, update both fields → verify both change
- [ ] T040 [US3] Test: Try to update non-existent ID 999 → verify "Task not found" error
- [ ] T041 [US3] Test: Try to update with empty title → verify error and title kept current

**Checkpoint**: User Stories 1, 2, AND 3 complete - Full task lifecycle (create, view, update, complete)

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Users can remove unwanted tasks to keep list clean

**Independent Test**: Create 3 tasks, delete task ID 2, verify only IDs 1 and 3 remain

### Implementation for User Story 4

**Business Logic**:
- [ ] T042 [US4] Implement TodoManager.delete_task(task_id: int) with TaskNotFoundError in src/services/todo_manager.py

**CLI Layer**:
- [ ] T043 [US4] Implement handle_delete_task(manager: TodoManager) function with ID prompt and confirmation message in src/cli/console.py

**Manual Validation for User Story 4**:
- [ ] T044 [US4] Test: Add 3 tasks, delete ID 2 → verify "Task 2 deleted successfully" message
- [ ] T045 [US4] Test: View tasks after delete → verify only IDs 1 and 3 remain
- [ ] T046 [US4] Test: Try to delete non-existent ID 999 → verify "Task not found" error
- [ ] T047 [US4] Test: Delete all tasks, view list → verify "No tasks found" message

**Checkpoint**: ALL user stories complete - Full CRUD + completion tracking functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, exit functionality, and comprehensive validation

**Integration**:
- [ ] T048 Wire handle_exit() or exit logic into run() main loop for menu option 6 in src/cli/console.py
- [ ] T049 Ensure all exception types are caught and displayed with user-friendly messages in all handlers in src/cli/console.py
- [ ] T050 Verify menu displays after every operation completes in src/cli/console.py

**Comprehensive Testing**:
- [ ] T051 Test full user journey: Add 5 tasks → Toggle some → Update some → Delete some → View final list
- [ ] T052 Test edge case: Add task with 200-char title → verify accepted
- [ ] T053 Test edge case: Add task with 201-char title → verify rejected
- [ ] T054 Test edge case: Add task with 1000-char description → verify accepted
- [ ] T055 Test edge case: Add task with 1001-char description → verify rejected
- [ ] T056 Test edge case: Rapid operations (add 100 tasks) → verify all have unique IDs and no performance degradation
- [ ] T057 Test edge case: Invalid menu choice (9) → verify error and menu redisplay
- [ ] T058 Test success criteria SC-001: Add task and view in ≤3 menu selections
- [ ] T059 Test success criteria SC-008: Restart application → verify task list empty (in-memory only)
- [ ] T060 Test success criteria SC-010: Clean startup and exit with option 6 → verify goodbye message

**Documentation**:
- [ ] T061 [P] Create or update README.md with user instructions (how to run, menu options, examples)
- [ ] T062 [P] Verify all planning artifacts reference correct file paths and are consistent with implementation

**Code Quality**:
- [ ] T063 Add type hints to all function signatures if missing
- [ ] T064 Add docstrings to all public functions and classes (Google style)
- [ ] T065 Review code for PEP 8 compliance (formatting, naming conventions)
- [ ] T066 Verify separation of concerns: TodoManager has no input()/print(), CLI has no business logic

**Final Validation**:
- [ ] T067 Run quickstart.md validation scenarios (Scenarios 1-5)
- [ ] T068 Verify all 10 success criteria (SC-001 through SC-010) from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies - start immediately
- **Phase 2: Foundational**: Depends on Phase 1 (Setup) - BLOCKS all user stories
- **Phase 3: User Story 1 (P1)**: Depends on Phase 2 (Foundational) - MVP delivery point
- **Phase 4: User Story 2 (P2)**: Depends on Phase 2 (Foundational) - Can run in parallel with US1 if desired, but sequentially is simpler
- **Phase 5: User Story 3 (P3)**: Depends on Phase 2 (Foundational) - Independent of US1/US2
- **Phase 6: User Story 4 (P4)**: Depends on Phase 2 (Foundational) - Independent of US1/US2/US3
- **Phase 7: Polish**: Depends on all user stories being complete

### User Story Dependencies

**Key Insight**: All user stories only depend on Phase 2 (Foundational). They do NOT depend on each other!

- **User Story 1 (P1)**: Can start immediately after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start immediately after Foundational - Independent (uses get_task and toggle_completion)
- **User Story 3 (P3)**: Can start immediately after Foundational - Independent (uses update_task)
- **User Story 4 (P4)**: Can start immediately after Foundational - Independent (uses delete_task)

### Within Each User Story

**Pattern for all stories**:
1. Business logic methods (TodoManager) before CLI handlers
2. CLI handlers before manual validation
3. Manual validation before marking story complete

**User Story 1 specific order**:
- T010-T014 (Business logic) can run in parallel [P] - different methods
- T015-T021 (CLI layer) depend on T010-T014 completion
- T022 (main.py) depends on T021
- T023-T026 (Manual tests) depend on T022

**User Story 2 specific order**:
- T027-T028 (Business logic) can run in parallel [P]
- T029 (CLI handler) depends on T027-T028
- T030-T034 (Manual tests) depend on T029

**User Story 3 specific order**:
- T035 (Business logic) first
- T036 (CLI handler) depends on T035
- T037-T041 (Manual tests) depend on T036

**User Story 4 specific order**:
- T042 (Business logic) first
- T043 (CLI handler) depends on T042
- T044-T047 (Manual tests) depend on T043

### Parallel Opportunities

**Within Phase 1 (Setup)**:
- T002 and T003 can run in parallel [P] after T001

**Within Phase 2 (Foundational)**:
- T005 and T006 can run in parallel [P] after T004
- T008 can run after T007
- T009 runs last

**Within User Story 1**:
- T010, T011, T012, T013 can all run in parallel [P] (different methods in todo_manager.py)
- T015, T016, T017 can run in parallel [P] (different functions in console.py)
- T018, T019 must wait for T015-T017 completion (need helper functions)

**Within User Story 2**:
- T027 and T028 can run in parallel [P] (different methods)

**Across User Stories** (if team has multiple developers):
- After Phase 2 completes:
  - Developer A: User Story 1 (T010-T026)
  - Developer B: User Story 2 (T027-T034)
  - Developer C: User Story 3 (T035-T041)
  - Developer D: User Story 4 (T042-T047)
- All stories converge at Phase 7 (Polish)

---

## Parallel Example: User Story 1

```bash
# After Phase 2 completes, launch all User Story 1 business logic methods in parallel:
Task: "T010 Create TodoManager class with __init__ in src/services/todo_manager.py"
Task: "T011 Implement TodoManager.add_task() in src/services/todo_manager.py"
Task: "T012 Implement TodoManager.get_all_tasks() in src/services/todo_manager.py"
Task: "T013 Implement TodoManager.task_count() in src/services/todo_manager.py"

# Then launch CLI helper functions in parallel:
Task: "T015 Create display_menu() function in src/cli/console.py"
Task: "T016 Create get_menu_choice() function in src/cli/console.py"
Task: "T017 Create get_integer_input() function in src/cli/console.py"

# Then implement handlers sequentially (they use helpers):
Task: "T018 Implement handle_add_task() in src/cli/console.py"
Task: "T019 Implement handle_view_tasks() in src/cli/console.py"
```

---

## Parallel Example: All User Stories (Team Strategy)

```bash
# Prerequisites: Phase 1 and Phase 2 complete

# Developer A (User Story 1 - MVP):
Task: "T010 through T026 - Create and View Tasks"

# Developer B (User Story 2 - Completion tracking):
Task: "T027 through T034 - Mark Tasks Complete/Incomplete"

# Developer C (User Story 3 - Updates):
Task: "T035 through T041 - Update Task Details"

# Developer D (User Story 4 - Deletion):
Task: "T042 through T047 - Delete Tasks"

# All developers converge:
Task: "T048 through T068 - Polish & Cross-Cutting Concerns"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Goal**: Deliverable working product with minimum features

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009) - CRITICAL blocker
3. Complete Phase 3: User Story 1 (T010-T026)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo MVP: Users can add and view tasks!

**Estimated Time**: ~2-3 hours for MVP
**Value Delivered**: Working todo app with core capture and review functionality

---

### Incremental Delivery (All User Stories)

**Goal**: Add features incrementally, testing each independently

1. Complete Setup + Foundational (T001-T009) → Foundation ready
2. Add User Story 1 (T010-T026) → Test independently → **Demo MVP!**
3. Add User Story 2 (T027-T034) → Test independently → **Demo completion tracking!**
4. Add User Story 3 (T035-T041) → Test independently → **Demo task editing!**
5. Add User Story 4 (T042-T047) → Test independently → **Demo full CRUD!**
6. Add Polish (T048-T068) → Final validation → **Demo production-ready app!**

**Estimated Time**: ~5-6 hours total
**Value**: Each story adds value without breaking previous stories

---

### Parallel Team Strategy (4 Developers)

**Goal**: Maximize throughput with parallel user story development

**Phase 1 & 2: All Together** (30-45 min)
- Entire team completes Setup and Foundational together
- Critical: Foundational MUST be complete before splitting

**Phase 3-6: Parallel by Story** (2-3 hours)
- Developer A: User Story 1 (P1) - MVP critical path
- Developer B: User Story 2 (P2) - Completion tracking
- Developer C: User Story 3 (P3) - Updates
- Developer D: User Story 4 (P4) - Deletion

**Phase 7: All Together** (1 hour)
- Entire team integrates and polishes
- Shared testing and validation

**Estimated Time**: ~4 hours with 4 developers
**Risk**: Requires good coordination; easier to do sequentially for solo work

---

## Task Summary

**Total Tasks**: 68
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (User Story 1 - P1): 17 tasks (10 implementation + 4 manual tests + integration)
- Phase 4 (User Story 2 - P2): 8 tasks (2 implementation + 5 manual tests + integration)
- Phase 5 (User Story 3 - P3): 7 tasks (2 implementation + 5 manual tests)
- Phase 6 (User Story 4 - P4): 6 tasks (2 implementation + 4 manual tests)
- Phase 7 (Polish): 21 tasks (integration + comprehensive testing + docs + code quality + final validation)

**Parallel Opportunities**: 14 tasks marked [P] (can run in parallel within constraints)

**MVP Scope**: Phases 1, 2, and 3 only (26 tasks, ~2-3 hours)

**Independent Test Criteria**:
- User Story 1: Add multiple tasks, view complete list with all details
- User Story 2: Create tasks, toggle completion, view updated statuses
- User Story 3: Create task, update title/description independently, verify changes
- User Story 4: Create 3 tasks, delete middle task, verify only 2 remain

---

## Notes

- **[P] tasks**: Different files or different methods in same file, no dependencies on incomplete tasks
- **[Story] label**: Maps task to specific user story for traceability (US1, US2, US3, US4)
- **No automated tests**: Spec requires manual acceptance testing only (unit tests optional)
- **Manual validation tasks**: Included to ensure each story meets acceptance criteria
- **Independent stories**: Each user story can be implemented and tested independently after Foundational phase
- **Checkpoint markers**: Stop points to validate story completion before proceeding
- **File paths**: All tasks include explicit file paths (src/models/task.py, src/services/todo_manager.py, etc.)
- **Type hints**: Required throughout (Python 3.13+ with typing support)
- **Separation of concerns**: TodoManager (no I/O), CLI (no business logic), enforced by task organization

**Recommended Approach**:
- Solo developer: Sequential (Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7)
- Team: Parallel after Foundational (each developer takes one user story)
- MVP delivery: Stop after Phase 3, validate, then decide whether to continue

**Success Validation**: Complete T067-T068 to verify all success criteria from spec.md are met.
