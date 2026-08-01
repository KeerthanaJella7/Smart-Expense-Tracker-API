# AI Assistance and Review Notes

This file records the parts of the project that were AI-assisted and the parts I reviewed or adjusted myself.

## What was AI-assisted

The initial implementation structure for this project was created with AI assistance. That included:

- the FastAPI route skeleton
- the initial Pydantic models
- the first version of the JSON storage helpers
- the base pytest test structure

## What I reviewed and changed

I manually reviewed the generated code and made several improvements to make it more reliable and easier to evaluate:

- added validation so empty titles and categories are rejected
- validated dates to ensure they follow the required YYYY-MM-DD format
- made category filtering case-insensitive
- added test isolation so each test uses a temporary storage file instead of mutating the shared JSON file
- improved the error responses for validation and not-found cases
- tightened delete-route validation so negative IDs are rejected as invalid input

## What I deliberately kept simple

I kept the implementation aligned with the assignment scope. I did not introduce a database, authentication, or a large abstraction layer because the project requirement specifically calls for a FastAPI API with JSON file storage and a simple test suite.

## Suggestions I rejected

I rejected a few ideas that would have made the project less aligned with the assignment:

- using an in-memory list as the main data store instead of a JSON file
- introducing SQLAlchemy or another database layer
- using UUIDs instead of auto-generated integer IDs

Those choices were rejected because they would have moved the project away from the required storage approach and API behavior.

## Honest summary

The core API and tests were completed, then reviewed and refined to improve correctness and clarity. The project is now more consistent, easier to run, and better documented than the initial draft.
