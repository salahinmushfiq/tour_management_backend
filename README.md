# 🌍 Tour Management Platform Backend

This is the Django REST API backend for the multi-organizer tour management platform.

## 🧱 Features

- JWT Authentication + Google OAuth
- Role-based permissions: Admin, Organizer, Tourist
- Tour event creation and participation
- Media sharing, cost tracking, and region logging
- Ready to be consumed by React, Flutter, or React Native apps

## 🚀 Quickstart

```bash
git clone https://github.com/yourusername/tour-management-backend.git
cd tour-management-backend

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp ..env .env

# Apply migrations and run server
python manage.py migrate
python manage.py runserver
```

## 🧩 Tech Stack

- Django + DRF
- PostgreSQL
- JWT (`djoser`, `simplejwt`)
- Cloudinary (media)
- Google Auth (`social-auth-app-django`)


# Authentication Module – TourMate Project

## Overview
The authentication module powers secure login, registration, and session management for the TourMate platform.

It supports:
- Email/password authentication  
- Google and Facebook OAuth social login  
- JWT-based access & refresh tokens  
- Role-based access control (Tourist, Organizer, Admin)  
- Password reset via email  
- Session expiration warnings with auto-refresh

This module protects APIs and personalizes user experiences across dashboards.

---

## Architecture
### Key Components

**Backend (Django + Djoser + SimpleJWT)**
- Custom `User` model with email as primary identifier  
- Role field (`tourist`, `organizer`, `admin`)  
- Endpoints for login, registration, token refresh, password reset  
- Social login with token exchange pipelines  

**Frontend (React + AuthContext)**
- Stores JWT tokens (access + refresh) in `localStorage`  
- Axios interceptors attach tokens & handle refresh  
- Session timer + modal warning for token expiry  
- Role-based redirects (`/dashboard/tourist`, `/dashboard/organizer`, `/dashboard/admin`)  

**Helper Files**
- `tokenService.js` → token storage and decoding  
- `authAPI.js` → wrapper for auth API calls  
- `useSessionTimer.js` → manages countdown & expiry modal

---

## Sequence Flows

### 1. Email/Password Login
```mermaid
sequenceDiagram
    participant U as User
    participant FE as React (AuthContext)
    participant BE as Django Backend
    participant DB as Database

    U->>FE: Submit email + password
    FE->>BE: POST /auth/jwt/create
    BE->>DB: Verify credentials
    DB-->>BE: Valid user
    BE-->>FE: JWT Access + Refresh
    FE->>FE: Save tokens (tokenService)
    FE->>FE: Redirect based on role
```

### 2. Social Login (Google/Facebook)
```mermaid
sequenceDiagram
    participant U as User
    participant FE as React SDK (Google/Facebook)
    participant BE as Django Backend
    participant Provider as OAuth Provider

    U->>FE: Login with Google/Facebook
    FE->>BE: Send provider token
    BE->>Provider: Verify token
    Provider-->>BE: User info
    BE->>BE: Get/Create user record
    BE-->>FE: JWT Access + Refresh
    FE->>FE: Save tokens & redirect
```

### 3. Token Refresh
```mermaid
sequenceDiagram
    participant FE as React (Axios Interceptor)
    participant BE as Django Backend

    FE->>BE: POST /auth/jwt/refresh (refresh token)
    BE-->>FE: New access token
    FE->>FE: Save new token (tokenService)
```

### 4. Password Reset
```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as Django Backend
    participant E as Email Service

    U->>FE: Request password reset
    FE->>BE: POST /auth/users/reset_password
    BE->>E: Send reset link with uid + token
    U->>FE: Open reset link
    FE->>BE: POST /auth/users/reset_password_confirm
    BE->>BE: Validate + update password
    BE-->>U: Password reset successful
```

---

## Security Considerations
- **JWT Expiry:** Short-lived access tokens (5–15 mins), long-lived refresh tokens (1–7 days)  
- **Refresh Rotation:** Each refresh invalidates the old refresh token  
- **Brute Force Protection:** Rate limiting login attempts via DRF throttling  
- **Email Verification:** Required before first login (if enabled)  
- **Secure Storage:** Tokens stored in localStorage, refresh guarded with short expiry + rotation  
- **HTTPS Only:** All tokens exchanged over TLS  
- **Role Validation:** Enforced at API level (IsAuthenticated, IsOrganizerOrAdmin, etc.)

---

## Endpoints Table
| Method | URL | Params / Body | Roles | Returns |
|--------|-----|---------------|-------|--------|
| POST | /auth/jwt/create/ | { email, password } | Any | { access, refresh } |
| POST | /auth/jwt/refresh/ | { refresh } | Authenticated | { access } |
| POST | /auth/jwt/verify/ | { token } | Authenticated | { "valid": true } |
| POST | /auth/users/ | { email, password, role } | Public | { id, email, role } |
| GET  | /auth/users/me/ | - | Authenticated | { id, email, role, profile } |
| POST | /auth/users/reset_password/ | { email } | Public | 200 OK (email sent) |
| POST | /auth/users/reset_password_confirm/ | { uid, token, new_password } | Public | 200 OK |
| POST | /auth/social/google/ | { token } | Public | { access, refresh } |
| POST | /auth/social/facebook/ | { token } | Public | { access, refresh } |

---

## Frontend Integration
**AuthContext.js (Core Responsibilities)**
- `login(email, password)` → calls /auth/jwt/create  
- `socialLogin(providerToken, provider)` → calls /auth/social/{provider}  
- `logout()` → clears tokens  
- `redirectToRoleDashboard()` → navigates user post-login  
- `axiosInstance` → pre-configured with interceptors for auto-refresh  
- Session modal → warns user before expiry, allows extending session

**Token Lifecycle**
1. Login → Save tokens in localStorage  
2. Axios sends access token with each request  
3. If access token expired → interceptor triggers refresh  
4. If refresh token expired → logout user

---

## UML Component Diagram
```mermaid
graph TD
    subgraph Frontend [React Frontend]
        FE[AuthContext.js]
        TS[tokenService.js]
        API[authAPI.js]
        TIMER[useSessionTimer.js]
    end

    subgraph Backend [Django Backend]
        DJ[Custom User Model]
        DJO[Djoser Endpoints]
        JWT[SimpleJWT]
        OAUTH[Google/Facebook Pipeline]
    end

    FE --> API
    TS --> FE
    TIMER --> FE
    API --> DJO
    DJO --> DJ
    DJO --> JWT
    DJO --> OAUTH
```

---

## Next Steps
- Expand Events Module documentation  
- Add Organizer Dashboard module  
- Add Tourist Dashboard module  
- Combine into full system doc with ERD + UML + API index

