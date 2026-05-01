TroyERP — Stale Project
Python · FastAPI · PostgreSQL · Redis · Temporal · Docker

Designed and built a modular, SAP-inspired ERP system from scratch with a microservices architecture. Key work included:

System Design: Modeled a 13-module ERP domain (SD, MM, FI, CO, PP, QM, PM, EWM, HCM, CS, TR, LE, RE-FX) covering Sales, Procurement, Finance, Production, Warehouse, and HR — with ER diagrams (Mermaid) documenting cross-module relationships.
Backend API: Built a RESTful API gateway with FastAPI, using SQLAlchemy ORM for async PostgreSQL access, and Pydantic schemas for request/response validation.
Database Layer: Designed a normalized PostgreSQL schema with shared master data tables (Customer, Vendor, Material, GL Account, Company Code, Cost Center) and transactional tables per module, with FK constraints and performance indexes.
Workflow Engine: Integrated Temporal for orchestrating complex, long-running business processes (e.g., Order-to-Cash, Purchase-to-Pay) with dedicated worker processes.
Infrastructure: Containerized the full stack with Docker Compose — PostgreSQL, Redis, Temporal server, and the FastAPI app running together locally.
This covers the main technical highlights.

I want it to be more towards forward deployed engineers.