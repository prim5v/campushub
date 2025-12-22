CampusHub Backend

CampusHub is a full-stack project with a backend powered by Flask. This repository contains the backend server, handling authentication, database operations, email verification, JWT-based sessions, rate limiting, and security features for a campus portal system.

Table of Contents

Features

Tech Stack

Project Structure

Setup

Environment Variables

Security

API Overview

License

Features

User Authentication: Email OTP verification, secure login with JWT.

Role-based Access: Supports comrade, landlord, e_service, and admin.

Device Tracking: Trust scores for user logins with alerts for unusual activity.

Rate Limiting: Protects endpoints from abuse.

Email Notifications: Security and informational alerts sent via SMTP.

CSRF Protection: Tokens for secure frontend-backend communication.

Database Management: MySQL integration with connection pooling and teardown.

Tech Stack

Backend Framework: Flask

Database: MySQL (via PyMySQL)

Authentication: JWT (PyJWT)

Email: Flask-Mail

Rate Limiting: Flask-Limiter

Environment Management: python-dotenv

Security: CSRF tokens, HTTPS-only cookies, hashed JWTs

Utilities: user-agents, Twilio, Google Generative AI API