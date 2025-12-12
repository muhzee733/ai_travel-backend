# API Endpoints & Payloads

All endpoints are under the `/api/` prefix. Authentication uses JWT (Authorization: Bearer `<access_token>`), except where noted.

## Auth (public)
- `POST /api/auth/register/` — Create a new customer account.  
  Body: `{"email": "...", "first_name": "...", "last_name": "...", "password": "...", "username": "<optional>"}`  
  Returns: user info.
- `POST /api/auth/login/` — Login with email/password.  
  Body: `{"email": "...", "password": "..."}`  
  Returns: user info + `access`, `refresh`.
- `POST /api/auth/token/refresh/` — Get a new access token.  
  Body: `{"refresh": "..."}`  
  Returns: new `access`.

## Dashboard (any authenticated user)
- `GET /api/dashboard/config/` — Returns user, roles, permission codes, filtered menu, and widgets based on permissions. No body.

## RBAC Admin (requires `rbac.manage_roles`)
- `GET /api/rbac/permissions/` — List permission catalog. No body.
- `GET /api/rbac/roles/` — List roles with permission codes. No body.
- `POST /api/rbac/roles/` — Create a role.  
  Body: `{"name": "...", "slug": "...", "description": "<optional>"}`.
- `PUT/PATCH /api/rbac/roles/{id}/` — Update a role.  
  Body: same as create (fields to change).
- `DELETE /api/rbac/roles/{id}/` — Delete a role.
- `PUT /api/rbac/roles/{id}/permissions/` — Replace permissions for a role.  
  Body: `{"permissions": ["hotels.view", "cars.view", ...]}` (must exist in catalog).

## User Role Assignment (requires `rbac.manage_roles`)
- `GET /api/rbac/users/?search=<term>` — List users (filtered by username/email/name). No body.
- `PUT /api/rbac/users/{id}/roles/` — Replace roles for a user.  
  Body: `{"roles": ["admin", "customer", ...]}` (role slugs).
