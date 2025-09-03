# Solution Steps

1. Refactor the database models (models.py) to normalize and define explicit one-to-many and many-to-one relationships between Users, Products, Orders, and OrderItems using foreign keys and constraints.

2. Introduce primary keys, foreign keys, unique constraints, and indexes as appropriate to ensure data integrity and fast queries.

3. Define Pydantic schemas (schemas.py) for API request/response—including OrderCreate, OrderOut, ProductOut, and nested order items—mirroring the normalized DB structure.

4. Configure async SQLAlchemy (database.py) with connection pooling and provide an async session dependency for FastAPI routes.

5. Rewrite CRUD logic (crud.py) for core DB operations—product listing, order creation, inventory updates—to use true async SQLAlchemy calls (including async select, update, commit).

6. Ensure correct and safe concurrent stock updates by using FOR UPDATE locking and atomic decrement in create_order, and wrap in a transaction.

7. Implement background inventory updates as FastAPI background tasks in main.py, using async DB sessions for deferred operations that do not block endpoint responses.

8. Adjust endpoint functions in main.py to use new async CRUD functions and background tasks, returning properly serialized Pydantic models.

9. Test with highly concurrent order creation; stock decrements/upserts are done transactionally and background tasks update inventory asynchronously, ensuring no slowdowns or race conditions.

10. Ensure all code is production-safe: commits are not done on error paths, relationships are cascaded, and fast queries are written using indexes and loading strategies.

