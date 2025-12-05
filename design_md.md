design.md

1.Overview
This project is a full-stack crypto trading simulation system that includes:

- Frontend (React)
- Backend API (FastAPI)
- Background Task Worker (redesigned using Celery)
- Redis (task/message broker)
- MongoDB (database managed with Beanie ODM)
- Binance WebSocket price stream
- Portfolio, credits, order handling, transaction history
- Chatbot integration for natural-language trading commands

The system now supports:

- Real-time price streaming
- Market & limit order execution
- Fully asynchronous background trade processing
- Atomic portfolio updates
- Credit updates and history tracking
- Stable cloud deployment (AWS Free Tier)

2.How the Software Design Was Improved

2.1 Decoupling API Requests from Trade Execution
Originally, the API endpoint executed trades synchronously. This caused:

- Long response times
- Worker timeouts
- Event loop issues
- User experience delays

Improvement:

- Trade logic moved into Celery background workers
- API endpoint only validates input and queues a task

Benefits:

- Faster responses
- Worker retry logic
- Proper asynchronous design
- Better error isolation

Improvement:

- Created `init_db_for_worker()`
- Ensures Beanie is initialized before Celery processes tasks

2.3 Atomic Portfolio Updates
Originally, portfolio updates were handled manually:

portfolio = await Portfolio.find_one(...)
portfolio.quantity += qty
await portfolio.save()

This created race conditions and duplicate key errors.

Improvement:
- Introduced **MongoDB atomic updates** using `$inc`, `$setOnInsert`
- Eliminated duplicate portfolio entry errors
- Added numerator tracking for correct average buy price

2.4 Standardizing Decimal Precision
Trading math originally used floating-point numbers.

Improvement:
- Introduced `quantize_decimal()` and `Decimal128` helpers
- Ensures MongoDB stores precise values
- Prevents rounding issues for fees, averages, totals

2.5 Worker Stability: Dramatiq -> Celery
Dramatiq caused:
- Event loop crashes
- Windows incompatibility
- Middleware import issues

Improvement:
- Migrated to Celery, which is stable, industry-standard, supports retries, and works cleanly with Redis

2.6 A complete cloud-ready deployment architecture was designed using Render (for backend services) and Vercel (for frontend hosting). This setup is scalable, easy to maintain, and suitable for production environments.

Architecture Overview
Backend (FastAPI API + Celery Worker + Redis + MongoDB) → Hosted on Render
Render Web Service → FastAPI backend
Render Worker Service → Celery worker
Render Redis → Message broker
MongoDB Atlas → Managed database
Frontend (React) → Deployed on Vercel
Reverse Proxy / SSL → Automatically handled by Render (backend) and Vercel (frontend)

Benefits:
Managed infrastructure → No need to configure servers manually
Scalable → Worker and web services can scale independently
Automatic SSL → Render + Vercel provide HTTPS by default
Cost-effective → Free tier available for both platforms
Production-grade deployment → Logs, monitoring, auto-restarts, and CI/CD
Separation of concerns → Frontend and backend independently deployable

3. Where Design Principles Were Applied

3.1 Single Responsibility Principle (SRP)
- API routes handle only validations & queuing
- Celery tasks handle trading logic
- Dedicated modules for portfolio updates
- Separate layer for credits history
- Chatbot logic decoupled from trade logic

3.2 Dependency Inversion
- API does not depend on Binance
- Worker encapsulates external API calls

3.3 DRY (Don't Repeat Yourself)
Centralized:
- Portfolio math
- Decimal conversions
- Trade fee logic
- DB initialization

3.4 Asynchronous Design
- Long-running trades handled by Celery
- Redis used as message broker
- WebSocket stream isolated from API

3.5 Error Isolation & Retry Patterns
- Errors in Binance or DB no longer break HTTP requests
- Celery provides robust retry capabilities

4. Key Refactoring Performed

4.1 Dramatiq Removal -> Celery Integration
- Dramatiq's import, worker lifecycle, and Windows issues were removed
- Celery provides supervised workers and built-in monitoring

4.2 Rewriting Worker Logic into a Clean Async Architecture
- Eliminated nested `asyncio.run()` calls
- Eliminated "Event loop is closed" errors

4.3 Atomic Portfolio Operations
- Eliminated all duplicate key errors
- Ensured consistency during concurrent trades

4.4 Clean Trade Execution Pipeline
Refactored trade steps into a deterministic workflow:
1. Queue task
2. Fetch user + validate credits
3. Fetch price
4. Execute order
5. Insert Order
6. Insert Transaction
7. Update Portfolio
8. Update Credits
9. Insert CreditsHistory

4..5 Deployment Restructuring (Render + Vercel)
Improved the deployment architecture by replacing local-only execution with a full cloud-ready configuration.

Added:
Render Web Service for FastAPI backend
Render Worker Service for Celery background processing
Render Redis as the message broker
MongoDB Atlas for managed database hosting
Vercel for frontend deployment (React/Vite)
Gunicorn + Uvicorn workers for production-grade ASGI serving
Automatic SSL certificates (handled by Render + Vercel)
Continuous Deployment pipelines via GitHub integration

Benefits:
Zero DevOps hosting
Auto-scaling worker and API services
Production-grade performance optimizations
Secure HTTPS by default
Clean separation between backend and frontend deployments

5. Architecture Diagram
                     ┌──────────────────┐
                     │     Vercel       │
                     │  (React Frontend)│
                     └──────────┬───────┘
                                │
                      HTTPS / CDN / Edge Network
                                │
                     ┌──────────▼──────────┐
                     │    Render Backend   │
                     │ (FastAPI Web API)   │
                     └──────────┬──────────┘
                                │
                         Trade Requests
                                │
               ┌─────────────────────────────────┐
               │                                 │
   ┌───────────▼──────────┐          ┌───────────▼──────────┐
   │   Render Worker       │          │   Render Redis        │
   │   Celery Background   │◄────────▶│   Task Queue Broker   │
   │   Trade Executor      │          │                       │
   └───────────┬──────────┘          └───────────┬──────────┘
               │                                  │
               │     Portfolio, Orders, Credits   │
               │                                  │
        ┌──────▼──────────────────────────────────▼──────┐
        │               MongoDB Atlas                     │
        │     (Users, Orders, Transactions, Portfolio)    │
        └─────────────────────────────────────────────────┘


Backend 
- FastAPI (Gunicorn + Uvicorn)
- Celery Worker
- Redis
- MongoDB
- WebSocket Listener
- Cron Jobs

6. Final Summary
The redesigned system is now:
- More scalable
- More maintainable
- More stable
- More cloud-ready
- Based on strong design principles

This file covers:
- How the system architecture evolved
- What improvements were made
- Why Celery replaced Dramatiq
- How principles like SRP, DRY, DIP were applied
- Major refactoring that improved performance and reliability.

